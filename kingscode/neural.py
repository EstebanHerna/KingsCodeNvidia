"""Open Qwen3 adapters with pinned revisions, exact cosine search and yes/no reranking.

Weights are loaded locally only by default. Run tools/prepare_neural.py to pin
and download the two allowlisted models. No hosted model APIs are used.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from .common import ROOT, file_hash, indexable, read_json, read_jsonl, write_json

ALLOWED = {"Qwen/Qwen3-Embedding-0.6B", "Qwen/Qwen3-Reranker-0.6B"}


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


class QwenEncoder:
    def __init__(self, config: dict | None = None):
        self.config = config or configuration()
        self.torch = setup(self.config)
        from transformers import AutoModel, AutoTokenizer
        name = self.config["embedding_model"]
        kwargs = model_args(name, self.config)
        self.tokenizer = AutoTokenizer.from_pretrained(name, padding_side="left", **kwargs)
        self.model = AutoModel.from_pretrained(name, dtype=getattr(self.torch, self.config["dtype"]),
                                              attn_implementation="eager", **kwargs).to(self.config["device"]).eval()

    def encode(self, texts: list[str], *, query: bool = False) -> np.ndarray:
        if query:
            texts = [f"Instruct: {self.config['instruction']}\nQuery: {t}" for t in texts]
        outputs = []
        batch = self.config["batch_size"]
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


def build_dense(corpus: Path) -> dict:
    cfg = configuration()
    passages = [p for p in read_jsonl(corpus / "passages.jsonl") if indexable(p)]
    encoder = QwenEncoder(cfg)
    vectors = encoder.encode([p["text"] for p in passages])
    path = corpus / "index/dense.npy"
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, vectors, allow_pickle=False)
    metadata = {"corpus_sha256": file_hash(corpus / "passages.jsonl"),
                "passage_ids": [p["passage_id"] for p in passages], "dimension": vectors.shape[1],
                "vectors_sha256": file_hash(path), "config": cfg,
                "model_lock": read_json(ROOT / "config/models.lock.json")[cfg["embedding_model"]]}
    write_json(corpus / "index/dense.meta.json", metadata)
    return {"vectors": len(vectors), "dimension": vectors.shape[1], "sha256": metadata["vectors_sha256"]}


class DenseIndex:
    def __init__(self, corpus: Path, passages: list[dict], corpus_sha256: str):
        path = corpus / "index/dense.meta.json"
        if not path.exists():
            raise RuntimeError("Dense index is missing; run tools/member_a.py dense")
        meta = read_json(path)
        if meta["corpus_sha256"] != corpus_sha256 or meta["passage_ids"] != [p["passage_id"] for p in passages]:
            raise ValueError("Dense index is stale or reordered")
        if meta["vectors_sha256"] != file_hash(corpus / "index/dense.npy"):
            raise ValueError("Dense vector hash mismatch")
        if meta["config"] != configuration():
            raise ValueError("Dense configuration changed; rebuild to avoid mismatched embeddings")
        if meta["model_lock"] != read_json(ROOT / "config/models.lock.json")[meta["config"]["embedding_model"]]:
            raise ValueError("Embedding revision changed; rebuild")
        self.vectors = np.load(corpus / "index/dense.npy", mmap_mode="r", allow_pickle=False)
        if self.vectors.shape != (len(passages), meta["dimension"]) or not np.isfinite(self.vectors).all():
            raise ValueError("Dense vectors invalid")
        self.encoder = QwenEncoder(meta["config"])
        self.passages = passages
        self._query, self._scores = None, None

    def all_scores(self, question):
        if self._query != question:
            self._scores = np.asarray(self.vectors @ self.encoder.encode([question], query=True)[0])
            self._query = question
        return self._scores

    def ranking(self, question, k):
        scores = self.all_scores(question)
        order = sorted(range(len(scores)), key=lambda i: (-float(scores[i]), self.passages[i]["passage_id"]))[:k]
        return order, {i: float(scores[i]) for i in order}

    def score_indices(self, question, indices):
        scores = self.all_scores(question)
        return {i: float(scores[i]) for i in indices}


class QwenReranker:
    def __init__(self, config=None):
        self.config = config or configuration()
        self.torch = setup(self.config)
        from transformers import AutoModelForCausalLM, AutoTokenizer
        name = self.config["reranker_model"]
        kwargs = model_args(name, self.config)
        self.tokenizer = AutoTokenizer.from_pretrained(name, padding_side="left", **kwargs)
        self.model = AutoModelForCausalLM.from_pretrained(name, dtype=getattr(self.torch, self.config["dtype"]),
                                                         attn_implementation="eager", **kwargs).to(self.config["device"]).eval()
        self.yes = self.tokenizer.convert_tokens_to_ids("yes")
        self.no = self.tokenizer.convert_tokens_to_ids("no")
        self.prefix = self.tokenizer.encode('<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be "yes" or "no".<|im_end|>\n<|im_start|>user\n', add_special_tokens=False)
        self.suffix = self.tokenizer.encode('<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n', add_special_tokens=False)

    def score(self, question: str, documents: list[str]) -> list[float]:
        output = []
        for start in range(0, len(documents), self.config["batch_size"]):
            docs = documents[start:start + self.config["batch_size"]]
            texts = [f"<Instruct>: {self.config['instruction']}\n<Query>: {question}\n<Document>: {doc}" for doc in docs]
            ids = self.tokenizer(texts, add_special_tokens=False, truncation=False)["input_ids"]
            ids = [self.prefix + row + self.suffix for row in ids]
            if any(len(row) > self.config["max_length"] for row in ids):
                raise ValueError("Reranker input exceeds max_length; no silent truncation")
            inputs = self.tokenizer.pad({"input_ids": ids}, padding=True, return_tensors="pt").to(self.model.device)
            with self.torch.inference_mode():
                logits = self.model(**inputs, logits_to_keep=1).logits[:, -1, [self.no, self.yes]].float()
                output.extend(self.torch.softmax(logits, dim=1)[:, 1].cpu().tolist())
        return output
