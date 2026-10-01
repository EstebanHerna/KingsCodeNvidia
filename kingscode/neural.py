"""Open Qwen3 adapters with pinned revisions, exact cosine search and yes/no reranking.

Weights are loaded locally only by default. Run tools/prepare_neural.py to pin
and download the two allowlisted models. No hosted model APIs are used.
"""
from __future__ import annotations

import os
import hashlib
from collections import OrderedDict
from pathlib import Path
from time import perf_counter

import numpy as np

from .common import ROOT, file_hash, indexable, read_json, read_jsonl, write_json
from .metadata import embedding_representation

ALLOWED = {"Qwen/Qwen3-Embedding-0.6B", "Qwen/Qwen3-Reranker-0.6B"}
QUERY_SCORE_CACHE_SIZE = 32


def configuration():
    return read_json(ROOT / "config/neural.json")


def setup(config: dict):
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    import torch
    torch.manual_seed(config["seed"])
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    if config["device"].startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but not available; diagnose the target machine")
    return torch


def model_args(model_id: str, config: dict) -> dict:
    if model_id not in ALLOWED:
        raise ValueError("Only approved open Qwen3 retrieval models may be loaded")
    lock_path = ROOT / "config/models.lock.json"
    if not lock_path.exists():
        raise RuntimeError("Missing model revisions. Run tools/prepare_neural.py first")
    lock = read_json(lock_path)
    revision = lock[model_id]["revision"]
    if len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise ValueError("Model revision must be an immutable commit SHA")
    return {"revision": revision, "cache_dir": str(ROOT / "models"),
            "local_files_only": config["local_files_only"], "trust_remote_code": False}


# SDPA instead of eager (2026-10-01): eager materializes heads x seq x seq per layer; with
# 4096-token reranker pairs next to the resident Qwen3-8B decoder (16.4 GB) on a 24 GB card that
# pushes Windows into silent system-RAM fallback (the decoder showed 46 GB reserved and 93 s/question
# with eager). Same math; differences are float rounding only. A dense index is still validated
# by config/model lock; rebuild it with this code before a freeze so documents and queries share kernels.
ATTN_IMPLEMENTATION = "sdpa"


class QwenEncoder:
    def __init__(self, config: dict | None = None):
        self.config = config or configuration()
        self.torch = setup(self.config)
        from transformers import AutoModel, AutoTokenizer
        name = self.config["embedding_model"]
        kwargs = model_args(name, self.config)
        self.tokenizer = AutoTokenizer.from_pretrained(name, padding_side="left", **kwargs)
        self.model = AutoModel.from_pretrained(name, dtype=getattr(self.torch, self.config["dtype"]),
                                              attn_implementation=ATTN_IMPLEMENTATION, **kwargs).to(self.config["device"]).eval()

    def encode(self, texts: list[str], *, query: bool = False, batch_size: int | None = None,
               instruction: str | None = None) -> np.ndarray:
        if query:
            task = instruction or self.config.get("embedding_instruction") or self.config["instruction"]
            texts = [f"Instruct: {task}\nQuery: {t}" for t in texts]
        outputs = []
        batch = batch_size or self.config["batch_size"]
        for offset in range(0, len(texts), batch):
            inputs = self.tokenizer(texts[offset:offset + batch], padding=True, truncation=False, return_tensors="pt")
            if inputs["input_ids"].shape[1] > self.config["max_length"]:
                raise ValueError("Embedding input exceeds max_length; rechunk or increase it explicitly")
            inputs = inputs.to(self.model.device)
            with self.torch.inference_mode():
                states = self.model(**inputs).last_hidden_state[:, -1]
                values = self.torch.nn.functional.normalize(states.float(), dim=1).cpu().numpy()
            outputs.append(values)
        return np.concatenate(outputs).astype("float32") if outputs else np.empty((0, self.model.config.hidden_size), dtype="float32")


BUILD_TOKEN_BUDGET = 32768   # tokens per batch when building the index (padding included)
BUILD_MAX_BATCH = 64


def encode_length_sorted(encoder, texts: list[str]) -> np.ndarray:
    """Index build only (queries are still encoded one by one). The config batch of 2 in
    corpus order spends most compute on padding (~13k tiny batches for 26.7k passages,
    ~1 h on a 4090). Sort by token length, fill batches up to a token budget, then restore
    the original order: same vectors up to float rounding, deterministic for a corpus."""
    lengths = [len(ids) for ids in encoder.tokenizer(texts, add_special_tokens=True, truncation=False)["input_ids"]]
    if any(n > encoder.config["max_length"] for n in lengths):
        raise ValueError("Embedding input exceeds max_length; rechunk or increase it explicitly")
    order = sorted(range(len(texts)), key=lambda i: (lengths[i], i))
    vectors, batch = [None] * len(texts), []

    def flush():
        if batch:
            out = encoder.encode([texts[i] for i in batch], batch_size=len(batch))
            for i, row in zip(batch, out):
                vectors[i] = row
            batch.clear()
    for i in order:
        if batch and ((len(batch) + 1) * lengths[i] > BUILD_TOKEN_BUDGET or len(batch) >= BUILD_MAX_BATCH):
            flush()
        batch.append(i)
    flush()
    return np.stack(vectors).astype("float32") if vectors else np.empty((0, encoder.model.config.hidden_size), dtype="float32")


def build_dense(corpus: Path) -> dict:
    cfg = configuration()
    passages = [p for p in read_jsonl(corpus / "passages.jsonl") if indexable(p)]
    encoder = QwenEncoder(cfg)
    vectors = encode_length_sorted(encoder, [p["text"] for p in passages])
    path = corpus / "index/dense.npy"
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, vectors, allow_pickle=False)
    metadata = {"corpus_sha256": file_hash(corpus / "passages.jsonl"),
                "passage_ids": [p["passage_id"] for p in passages], "dimension": vectors.shape[1],
                "vectors_sha256": file_hash(path), "config": cfg,
                "model_lock": read_json(ROOT / "config/models.lock.json")[cfg["embedding_model"]]}
    write_json(corpus / "index/dense.meta.json", metadata)
    return {"vectors": len(vectors), "dimension": vectors.shape[1], "sha256": metadata["vectors_sha256"]}


def build_context_dense(corpus: Path, output_dir: Path) -> dict:
    """Build an isolated dense index over structural search text, never corpus evidence.

    The index is tied to the literal corpus hash and stable passage order. It lives
    outside corpus/index and therefore cannot silently replace the frozen baseline.
    """
    cfg = configuration()
    passages = [p for p in read_jsonl(corpus / "passages.jsonl") if indexable(p)]
    texts = [embedding_representation(p) for p in passages]
    encoder = QwenEncoder(cfg)
    vectors = encode_length_sorted(encoder, texts)
    output_dir.mkdir(parents=True, exist_ok=True)
    vector_path = output_dir / "dense.npy"
    np.save(vector_path, vectors, allow_pickle=False)
    metadata = {"representation_id": "context_metadata_v1",
                "corpus_sha256": file_hash(corpus / "passages.jsonl"),
                "passage_ids": [p["passage_id"] for p in passages],
                "dimension": vectors.shape[1], "vectors_sha256": file_hash(vector_path),
                "search_text_sha256": hashlib.sha256("\n".join(texts).encode("utf-8")).hexdigest(),
                "config": cfg,
                "model_lock": read_json(ROOT / "config/models.lock.json")[cfg["embedding_model"]]}
    write_json(output_dir / "dense.meta.json", metadata)
    return {"vectors": len(vectors), "dimension": vectors.shape[1],
            "representation_id": metadata["representation_id"], "sha256": metadata["vectors_sha256"]}


class DenseIndex:
    def __init__(self, corpus: Path, passages: list[dict], corpus_sha256: str, *,
                 index_dir: str | Path | None = None, query_instruction: str | None = None,
                 representation_id: str = "source_text_v1"):
        index_dir = Path(index_dir) if index_dir else corpus / "index"
        path = index_dir / "dense.meta.json"
        if not path.exists():
            raise RuntimeError("Dense index is missing; run tools/member_a.py dense")
        meta = read_json(path)
        stored_representation = meta.get("representation_id", "source_text_v1")
        if stored_representation != representation_id:
            raise ValueError("Dense index representation does not match retrieval_text_mode")
        if meta["corpus_sha256"] != corpus_sha256 or meta["passage_ids"] != [p["passage_id"] for p in passages]:
            raise ValueError("Dense index is stale or reordered")
        if meta["vectors_sha256"] != file_hash(index_dir / "dense.npy"):
            raise ValueError("Dense vector hash mismatch")
        if meta["config"] != configuration():
            raise ValueError("Dense configuration changed; rebuild to avoid mismatched embeddings")
        if representation_id == "context_metadata_v1":
            context_texts = [embedding_representation(p) for p in passages]
            context_hash = hashlib.sha256("\n".join(context_texts).encode("utf-8")).hexdigest()
            if meta.get("search_text_sha256") != context_hash:
                raise ValueError("Context dense index was built from a different structural search view")
        if meta["model_lock"] != read_json(ROOT / "config/models.lock.json")[meta["config"]["embedding_model"]]:
            raise ValueError("Embedding revision changed; rebuild")
        self.vectors = np.load(index_dir / "dense.npy", mmap_mode="r", allow_pickle=False)
        if self.vectors.shape != (len(passages), meta["dimension"]) or not np.isfinite(self.vectors).all():
            raise ValueError("Dense vectors invalid")
        self.encoder = QwenEncoder(meta["config"])
        self.query_instruction = query_instruction
        self.passages = passages
        # A router-enabled pipeline may retrieve OFF and then ON for the same
        # query/views. Keep a small score cache so the second pass does not
        # encode those exact queries again; the cache is bounded for larger corpora.
        self._score_cache = OrderedDict()
        self.last_query_profile = {"encoded_queries": 0, "encode_batches": 0}

    def all_scores(self, question):
        if question in self._score_cache:
            self._score_cache.move_to_end(question)
            return self._score_cache[question]
        scores = np.asarray(self.vectors @ self.encoder.encode([question], query=True,
                                                               instruction=self.query_instruction)[0])
        self._score_cache[question] = scores
        if len(self._score_cache) > QUERY_SCORE_CACHE_SIZE:
            self._score_cache.popitem(last=False)
        return scores

    def ranking(self, question, k):
        scores = self.all_scores(question)
        order = sorted(range(len(scores)), key=lambda i: (-float(scores[i]), self.passages[i]["passage_id"]))[:k]
        return order, {i: float(scores[i]) for i in order}

    def ranking_many(self, questions: list[str], k: int):
        """Encode uncached query views together, then rank each against the index."""
        missing, seen = [], set()
        for question in questions:
            if question not in self._score_cache and question not in seen:
                missing.append(question)
                seen.add(question)
        batch_size = self.encoder.config["batch_size"]
        self.last_query_profile = {
            "encoded_queries": len(missing),
            "encode_batches": ((len(missing) + batch_size - 1) // batch_size if missing else 0),
        }
        if missing:
            embeddings = self.encoder.encode(missing, query=True, instruction=self.query_instruction)
            for question, embedding in zip(missing, embeddings):
                self._score_cache[question] = np.asarray(self.vectors @ embedding)
                if len(self._score_cache) > QUERY_SCORE_CACHE_SIZE:
                    self._score_cache.popitem(last=False)
        return [self.ranking(question, k) for question in questions]

    def score_indices(self, question, indices):
        scores = self.all_scores(question)
        return {i: float(scores[i]) for i in indices}

    def option_support(self, question: str, options: dict[str, str], passages: list[dict]) -> dict[str, dict[str, float]]:
        """Auxiliary cosine scores for Q+option against final evidence (never a selector)."""
        started = perf_counter()
        if not isinstance(options, dict) or any(not isinstance(k, str) or not isinstance(v, str)
                                                for k, v in options.items()):
            raise ValueError("option support requires a plain option mapping")
        positions = {p["passage_id"]: i for i, p in enumerate(self.passages)}
        try:
            indices = [positions[p["passage_id"]] for p in passages]
        except KeyError as exc:
            raise ValueError("Final evidence contains a passage absent from the dense index") from exc
        views = [f"{question}\nCandidate option {letter}: {text}" for letter, text in sorted(options.items())]
        query_vectors = self.encoder.encode(views, query=True, instruction=self.query_instruction)
        doc_vectors = np.asarray(self.vectors[indices], dtype="float32")
        scores = query_vectors @ doc_vectors.T
        result = {letter: {p["passage_id"]: float(scores[option_index, passage_index])
                           for passage_index, p in enumerate(passages)}
                  for option_index, (letter, _) in enumerate(sorted(options.items()))}
        self.last_option_support_ms = round((perf_counter() - started) * 1000, 3)
        return result


class QwenReranker:
    def __init__(self, config=None, *, batch_size: int | None = None, instruction: str | None = None):
        self.config = dict(config or configuration())
        if instruction is not None:
            if not isinstance(instruction, str) or not instruction.strip():
                raise ValueError("reranker instruction must be nonempty plain text")
            self.config["reranker_instruction"] = instruction.strip()
        self.batch_size = int(batch_size or self.config["batch_size"])
        if self.batch_size < 1:
            raise ValueError("reranker batch_size must be positive")
        self.torch = setup(self.config)
        from transformers import AutoModelForCausalLM, AutoTokenizer
        name = self.config["reranker_model"]
        kwargs = model_args(name, self.config)
        self.tokenizer = AutoTokenizer.from_pretrained(name, padding_side="left", **kwargs)
        self.model = AutoModelForCausalLM.from_pretrained(name, dtype=getattr(self.torch, self.config["dtype"]),
                                                         attn_implementation=ATTN_IMPLEMENTATION, **kwargs).to(self.config["device"]).eval()
        self.yes = self.tokenizer.convert_tokens_to_ids("yes")
        self.no = self.tokenizer.convert_tokens_to_ids("no")
        self.prefix = self.tokenizer.encode('<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n', add_special_tokens=False)
        self.suffix = self.tokenizer.encode('<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n', add_special_tokens=False)

    def score(self, question: str, documents: list[str]) -> list[float]:
        output = []
        ids = _prepare_reranker_input_ids(self.tokenizer, question, documents, self.config,
                                          self.prefix, self.suffix)
        for start in range(0, len(documents), self.batch_size):
            batch_ids = ids[start:start + self.batch_size]
            inputs = self.tokenizer.pad({"input_ids": batch_ids}, padding=True, return_tensors="pt").to(self.model.device)
            with self.torch.inference_mode():
                logits = self.model(**inputs, logits_to_keep=1).logits[:, -1, [self.no, self.yes]].float()
                output.extend(self.torch.softmax(logits, dim=1)[:, 1].cpu().tolist())
        return output


def _prepare_reranker_input_ids(tokenizer, question: str, documents: list[str], config: dict,
                                prefix: list[int], suffix: list[int]) -> list[list[int]]:
    """Tokenize and validate every pair before any reranker forward pass.

    This avoids scoring early mini-batches only to discover an overlength pair
    near the end, after which the safe retrieval wrapper must rerun without the
    reranker. Tokenization is also issued once per candidate set instead of once
    per GPU mini-batch; model forwards remain bounded by config.batch_size.
    """
    instruction = config.get("reranker_instruction") or config.get("instruction")
    texts = [f"<Instruct>: {instruction}\n<Query>: {question}\n<Document>: {doc}" for doc in documents]
    rows = tokenizer(texts, add_special_tokens=False, truncation=False)["input_ids"]
    ids = [prefix + row + suffix for row in rows]
    if any(len(row) > config["max_length"] for row in ids):
        raise ValueError("Reranker input exceeds max_length; no silent truncation")
    return ids
