"""Verified neural execution for the internal benchmark; never downloads weights.

Encoder identity is a registry entry, separate from variant composition. Adding
an encoder requires an approved lock/loader/index, not another evaluator.
"""
from __future__ import annotations

from pathlib import Path
import time

from .common import ROOT, file_hash, read_json
from .model_assets import resolve_model, verify_snapshot
from .retrieval import Retriever

ENCODERS = {"QWEN": "Qwen/Qwen3-Embedding-0.6B"}
RERANKER = "Qwen/Qwen3-Reranker-0.6B"
EXECUTABLE = ("R1-QWEN", "R2-QWEN", "R3", "R4", "R5", "R6", "R7", "R8")


def variant_config(variant: str) -> dict:
    if variant not in EXECUTABLE:
        raise ValueError(f"No approved neural implementation for {variant}")
    config = {"mode": "dense" if variant == "R1-QWEN" else "hybrid",
              "rerank": variant not in {"R1-QWEN", "R2-QWEN"},
              "encoder": "QWEN", "graph_mode": "off", "graph_budget": 10,
              "candidate_k": 30, "k_metrics": 10, "evidence_k": 8,
              "rrf_constant": 60, "seed": 0, "diagnostic": False,
              "query_transform": "none; safe question text only"}
    if variant in {"R4", "R5"}:
        config["graph_mode"] = "auto" if variant == "R4" else "on"
    if variant in {"R6", "R7", "R8"}:
        config["experiment"] = variant
        config["effective_parameters"] = {
            "R6": {"candidate_multiplier": 4},
            "R7": {"doc_pool": 24},
            "R8": {"level": "document", "max_per_group": 2},
        }[variant]
        # Preserve existing run_experiment(..., k=30) contracts, including its
        # expanded pool. Do not misreport this pool as candidate_k=30.
        config["experiment_requested_k"] = 30
        config["effective_pool_k"] = 30 if variant == "R7" else 120
    return config


def validate_base_run(path: Path | None, manifest_sha: str, corpus_identity: dict) -> dict:
    if path is None:
        raise ValueError("R3-R8 require --base-run from an explicitly chosen R2-QWEN validation run")
    from .benchmark_analysis import load_run
    report, _ = load_run(path)
    if (report.get("variant") != "R2-QWEN" or report.get("split") != "validation"
            or report.get("benchmark", {}).get("manifest_sha256") != manifest_sha
            or report.get("corpus") != corpus_identity
            or report.get("config") != variant_config("R2-QWEN")
            or report.get("execution", {}).get("verified_real_backend") is not True):
        raise ValueError("Base must be a verified R2-QWEN validation run of this benchmark/corpus")
    return {"variant": "R2-QWEN", "selection_split": "validation",
            "report_sha256": file_hash(path / "report.json"),
            "execution_identity": report["execution_identity"]}


class NoLexicalRanking:
    """R1 performs no BM25 scoring, despite the shared Retriever interface."""
    def ranking(self, question, k):
        return [], {}


def preflight(corpus: Path, config: dict) -> dict:
    from .neural import configuration
    neural = configuration()
    if not neural.get("device", "").startswith("cuda"):
        raise RuntimeError("CUDA_REQUIRED: configure retrieval explicitly for the target GPU")
    if neural.get("dtype") != "bfloat16" or neural.get("seed") != 0:
        raise ValueError("Benchmark requires explicit BF16 and seed 0")
    if neural.get("local_files_only") is not True:
        raise ValueError("Offline snapshots required; silent downloads are forbidden")
    if neural.get("embedding_model") != ENCODERS[config["encoder"]]:
        raise ValueError("Encoder substitution is forbidden")
    if config["rerank"] and neural.get("reranker_model") != RERANKER:
        raise ValueError("Reranker substitution is forbidden")
    for name in ("dense.npy", "dense.meta.json"):
        if not (corpus / "index" / name).is_file():
            raise FileNotFoundError(f"DENSE_INDEX_MISSING: corpus/index/{name}")
    models = {"encoder": verify_snapshot(resolve_model(neural["embedding_model"]))}
    if config["rerank"]:
        models["reranker"] = verify_snapshot(resolve_model(neural["reranker_model"]))
    return {"neural_config": neural, "models": models,
            "dense_sha256": file_hash(corpus / "index/dense.npy"),
            "dense_meta_sha256": file_hash(corpus / "index/dense.meta.json")}


def verify_loaded_backend(retriever, config, torch):
    from .neural import DenseIndex, QwenEncoder, QwenReranker
    if not isinstance(retriever, Retriever) or not isinstance(retriever.dense, DenseIndex):
        raise RuntimeError("UNVERIFIED_BACKEND: real DenseIndex required")
    if not isinstance(retriever.dense.encoder, QwenEncoder):
        raise RuntimeError("UNVERIFIED_BACKEND: real QwenEncoder required")
    models = [retriever.dense.encoder.model]
    if config["rerank"]:
        if not isinstance(retriever.reranker, QwenReranker):
            raise RuntimeError("UNVERIFIED_BACKEND: real QwenReranker required")
        models.append(retriever.reranker.model)
    elif retriever.reranker is not None:
        raise RuntimeError("Unexpected reranker")
    device = torch.device(retriever.dense.encoder.config["device"])
    if device.index is None:
        device = torch.device("cuda", torch.cuda.current_device())
    for model in models:
        if not isinstance(model, torch.nn.Module):
            raise RuntimeError("UNVERIFIED_BACKEND: loaded torch module required")
        parameters = list(model.parameters())
        if not parameters or any(p.device.type != "cuda" or
                                p.device.index != device.index or p.dtype != torch.bfloat16
                                for p in parameters):
            raise RuntimeError("UNVERIFIED_BACKEND: actual CUDA/BF16 parameters required")


class NeuralRuntime:
    def __init__(self, corpus: Path, config: dict):
        started = time.perf_counter()
        self.config = config
        self.assets = preflight(corpus, config)
        from .neural import setup
        self.torch = setup(self.assets["neural_config"])
        self.device = self.torch.device(self.assets["neural_config"]["device"])
        if self.device.index is None:
            self.device = self.torch.device("cuda", self.torch.cuda.current_device())
        with self.torch.cuda.device(self.device):
            if not self.torch.cuda.is_bf16_supported():
                raise RuntimeError("BF16_NOT_SUPPORTED")
        self.torch.cuda.reset_peak_memory_stats(self.device)
        from .reasoning.routing import RetrieverGraphRouter
        self.adapter = RetrieverGraphRouter()
        self.retriever = Retriever(corpus, mode=config["mode"], rerank=config["rerank"],
                                   candidate_k=config["candidate_k"], graph_budget=config["graph_budget"],
                                   graph_router=self.adapter)
        if config["mode"] == "dense":
            self.retriever.bm25 = NoLexicalRanking()
        verify_loaded_backend(self.retriever, config, self.torch)
        self.sync()
        self.initialization_seconds = time.perf_counter() - started

    def sync(self):
        self.torch.cuda.synchronize(self.device)

    def record(self):
        verify_loaded_backend(self.retriever, self.config, self.torch)
        return {"verified_real_backend": True, **self.assets,
                "initialization_seconds": self.initialization_seconds,
                "hardware": {"device": str(self.device), "torch_version": self.torch.__version__,
                             "torch_cuda_runtime": self.torch.version.cuda,
                             "gpu_name": self.torch.cuda.get_device_name(self.device)},
                "peak_vram_bytes": self.torch.cuda.max_memory_allocated(self.device)}

    def retrieve(self, text: str, k: int):
        from .metadata_experiments import run_experiment
        if "experiment" in self.config:
            return run_experiment(self.config["experiment"], self.retriever, text, k,
                                  **self.config["effective_parameters"])
        mode = self.config["graph_mode"]
        if mode == "auto":
            from .reasoning.routing import route_graph
            flat = self.retriever.retrieve(text, k, "off")
            decision = route_graph(text, flat)
            self.adapter.bind(text, decision)
            # Preserve requested AUTO in passage provenance, and let the bound
            # deterministic policy alone decide whether expansion is active.
            return self.retriever.retrieve(text, k, "auto")
        return self.retriever.retrieve(text, k, mode)


def execution_identity(config: dict, assets: dict, source: dict) -> dict:
    """Portable comparison identity, excluding machine paths, time and split."""
    return {"config": config, "neural_config": assets["neural_config"],
            "models": {role: {k: value[k] for k in ("repo_id", "revision", "manifest_sha256")}
                       for role, value in assets["models"].items()},
            "dense_sha256": assets["dense_sha256"], "dense_meta_sha256": assets["dense_meta_sha256"],
            "source_identity": source}
