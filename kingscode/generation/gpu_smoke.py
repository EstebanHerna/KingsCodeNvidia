"""Future real GPU smoke. No state flags are updated, including on success."""
from __future__ import annotations

from datetime import datetime, timezone
import gc
from pathlib import Path
from time import perf_counter

from ..common import ROOT, read_json, read_jsonl, write_json
from ..gpu_environment import require_cuda
from ..model_assets import RETRIEVAL, resolve_model, verify_snapshot
from .config import load_bakeoff
from .experiments import run_generation, smoke_input


def run_gpu_smoke(alias="qwen3-8b", *, output_root=ROOT / "reports/gpu_smoke", torch_module=None,
                  precision="bf16", oom_record: Path | None = None) -> dict:
    record = {"status": "running", "model": alias, "scope": "real GPU smoke only; not a full benchmark", "stages": []}
    started = perf_counter()
    torch = None
    phase = "cuda_check"
    try:
        if torch_module is None:
            try:
                import torch
            except ImportError as exc:
                raise RuntimeError("CUDA_NOT_AVAILABLE") from exc
        else:
            torch = torch_module
        require_cuda(torch)
        torch.cuda.reset_peak_memory_stats(0)
        record["runtime"] = {"torch": torch.__version__, "torch_cuda": torch.version.cuda,
                             "gpu": torch.cuda.get_device_properties(0).name}
        cfg = load_bakeoff()
        record["decoder_config"] = cfg["candidates"][alias]
        record["precision"] = precision
        # Verify cache before allocating models. No network permitted here.
        record["assets"] = [verify_snapshot(resolve_model(name), ROOT / cfg["cache_dir"]) for name in (*RETRIEVAL, alias)]
        stage = perf_counter()
        phase = "bf16_matmul"
        a = torch.ones((64, 64), device="cuda:0", dtype=torch.bfloat16)
        product = a @ a
        torch.cuda.synchronize()
        if product[0, 0].item() != 64:
            raise RuntimeError("BF16_MATMUL_FAILED")
        record["stages"].append({"stage": "bf16_matmul", "seconds": perf_counter() - stage,
                                 "peak_vram_bytes": torch.cuda.max_memory_allocated(0)})
        del a, product
        from ..neural import QwenEncoder, QwenReranker
        neural = read_json(ROOT / "config/neural.json")
        neural.update(device="cuda:0", dtype="bfloat16", batch_size=1, local_files_only=True)
        record["neural_config"] = neural
        question, evidence = smoke_input()
        texts = [p["text"] for p in read_json(ROOT / "tests/fixtures/member_b_official_passages.json")[:2]]
        stage = perf_counter()
        phase = "embedding"
        encoder = QwenEncoder(neural)
        vectors = encoder.encode(texts)
        query = encoder.encode([question.text], query=True)
        import numpy as np
        if vectors.shape[0] != 2 or not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5):
            raise RuntimeError("EMBEDDING_SMOKE_FAILED")
        torch.cuda.synchronize()
        record["stages"].append({"stage": "embedding", "seconds": perf_counter() - stage,
                                 "shape": list(vectors.shape), "query_shape": list(query.shape),
                                 "peak_vram_bytes": torch.cuda.max_memory_allocated(0)})
        del encoder
        gc.collect(); torch.cuda.empty_cache()
        stage = perf_counter()
        phase = "reranker"
        reranker = QwenReranker(neural)
        scores = reranker.score(question.text, texts)
        if len(scores) != 2 or not all(0 <= s <= 1 for s in scores):
            raise RuntimeError("RERANKER_SMOKE_FAILED")
        torch.cuda.synchronize()
        record["stages"].append({"stage": "reranker", "seconds": perf_counter() - stage, "scores": scores,
                                 "peak_vram_bytes": torch.cuda.max_memory_allocated(0)})
        del reranker
        gc.collect(); torch.cuda.empty_cache()
        stage = perf_counter()
        phase = "decoder_and_guards"
        experiment = run_generation(alias, mode="decoder-smoke", output_root=output_root / "decoder",
                                     precision=precision, oom_record=oom_record)
        record["decoder_experiment"] = experiment
        if experiment["status"] != "passed":
            raise RuntimeError(experiment.get("error", {}).get("code", "DECODER_SMOKE_FAILED"))
        row = read_jsonl(Path(experiment["paths"]["submission"]))[0]
        record["stages"].append({"stage": "decoder_and_guards", "seconds": perf_counter() - stage,
                                 "peak_vram_bytes": experiment["metrics"]["peak_vram_bytes"]})
        record.update(status="passed", submission=row)
    except Exception as exc:
        record.update(status="failed", error={"type": type(exc).__name__, "code": getattr(exc, "code", str(exc)),
                                               "phase": phase, "detail": getattr(exc, "detail", {})})
        if "out of memory" in str(exc).lower():
            record["error"]["code"] = "CUDA_OOM"
    finally:
        record["total_seconds"] = perf_counter() - started
        record["peak_vram_bytes"] = max((s["peak_vram_bytes"] for s in record["stages"] if s["peak_vram_bytes"] is not None), default=None)
        try:
            if torch is not None and torch.cuda.is_available():
                record["peak_vram_bytes"] = max(record["peak_vram_bytes"] or 0, torch.cuda.max_memory_allocated(0))
        except Exception as exc:
            record["memory_error_type"] = type(exc).__name__
        record["project_state_modified"] = False
        path = output_root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
        write_json(path, record)
        record["report"] = str(path.resolve())
    return record
