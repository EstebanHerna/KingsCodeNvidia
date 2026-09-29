"""Real decoder experiments, isolated from the immutable Gate 1B dummy runner."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.metadata
from pathlib import Path
import platform
import statistics
import sys
from time import perf_counter

from ..common import ROOT, file_hash, read_json, write_json, write_jsonl
from ..reasoning.contracts import Question, public_question
from ..reasoning.evaluation import official_hashes, run_eval
from ..reasoning.experiments import fingerprint
from ..reasoning.guards import CitationGuardError
from ..reasoning.pipeline import _answer
from .config import load_bakeoff, select_decoder
from .hf_decoder import DecoderFailure, HFDecoder
from .retrieval_experiments import corpus_identity, load_freeze


def smoke_input():
    # Literal existing official evidence, no expected answers or generated dataset.
    passage = read_json(ROOT / "tests/fixtures/member_b_official_passages.json")[1]
    return Question(0, "¿Cuál es el objeto del artículo 1 de la Ley 1010 de 2006?", "semi_open"), [passage]


def validate_fallback(precision: str, previous: Path | None, comparison: dict):
    if precision == "bf16":
        return
    if previous is None:
        raise ValueError("Explicit quantization requires --oom-record from the matching BF16 run")
    old = read_json(previous)
    if (old.get("status") != "failed" or old.get("precision") != "bf16"
            or old.get("error", {}).get("code") != "CUDA_OOM" or old.get("comparison") != comparison):
        raise ValueError("Fallback requires a matching BF16 OOM: same model, revision, evidence, context, prompt and generation config")


def run_generation(alias: str, *, mode="sample", config_path=ROOT / "config/decoder_bakeoff.json",
                   freeze_path: Path | None = None, output_root=ROOT / "reports/decoders", precision="bf16",
                   oom_record: Path | None = None, allow_optional=False, backend=None, corpus: Path = ROOT / "corpus") -> dict:
    cfg = load_bakeoff(config_path)
    candidate = select_decoder(alias, cfg, allow_optional=allow_optional)
    if mode not in {"sample", "decoder-smoke"}:
        raise ValueError("Unsupported decoder experiment")
    directory = output_root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + alias + "-" + precision)
    directory.mkdir(parents=True, exist_ok=False)
    record = {"status": "running", "model": alias, "revision": candidate["revision"], "precision": precision,
              "mode": mode, "candidate": candidate, "prompt_version": cfg["prompt_version"],
              "generation_config": cfg["generation"], "max_new_tokens": cfg["max_new_tokens"],
              "runtime": {"python": sys.version, "platform": platform.platform(),
                          "kind": "injected_unit_backend" if backend is not None else "real_local_transformers"},
              "paths": {"run": str(directory.resolve()), "submission": str((directory / "submissions.jsonl").resolve())},
              "official_evaluation": None, "ragas": {"status": "not_run_requires_separate_authorization_and_key"}}
    decoder = None
    rows, traces, inputs, times = [], [], [], []
    attempted = called = json_valid = citation_count = unsupported = 0
    started = perf_counter()
    try:
        record["official_hashes"] = official_hashes()
        record["corpus"] = corpus_identity(corpus)
        if mode == "sample":
            path = freeze_path or ROOT / cfg["retrieval_freeze"]
            frozen = load_freeze(path, corpus=corpus)
            inputs = [(public_question(r["question"]), r["passages"]) for r in frozen["records"]]
            evidence_identity = {"sha256": file_hash(path), "fingerprint": frozen["fingerprint"],
                                 "retrieval_config": frozen["retrieval_config"], "path": str(path.resolve())}
        else:
            inputs = [smoke_input()]
            evidence_identity = {"sha256": fingerprint([{"question": q.public_record(), "passages": p} for q, p in inputs]),
                                 "scope": "one literal source smoke; not a sample score"}
        record["evidence"] = evidence_identity
        record["comparison"] = {"model": alias, "candidate": candidate, "generation": cfg["generation"],
                                "max_new_tokens": cfg["max_new_tokens"], "prompt_version": cfg["prompt_version"],
                                "evidence_sha256": evidence_identity["sha256"], "corpus": record["corpus"]}
        validate_fallback(precision, oom_record, record["comparison"])
        record["fallback_from"] = str(oom_record.resolve()) if oom_record else None
        record["implementation_sha256"] = {p.relative_to(ROOT).as_posix(): file_hash(p)
                                             for folder in (ROOT / "kingscode/generation", ROOT / "kingscode/reasoning")
                                             for p in sorted(folder.glob("*.py"))}
        record["fingerprint"] = fingerprint({"comparison": record["comparison"], "precision": precision,
                                             "implementation": record["implementation_sha256"]})
        write_jsonl(directory / "questions.jsonl", [q.public_record() for q, _ in inputs])
        decoder = backend or HFDecoder(alias, config=cfg, precision=precision, allow_optional=allow_optional)
        for question, passages in inputs:
            attempted += 1
            decoder.last_usage = {}
            start = perf_counter()
            try:
                row, trace = _answer(question, passages, decoder)
            except Exception:
                usage = dict(getattr(decoder, "last_usage", {}))
                if usage:
                    called += 1
                    json_valid += int(bool(usage.get("json_valid")))
                traces.append({"id": question.id, "status": "failed", "generation": usage,
                               "latency_ms": (perf_counter() - start) * 1000})
                raise
            usage = dict(getattr(decoder, "last_usage", {}))
            called += int(bool(usage))
            json_valid += int(not usage or bool(usage.get("json_valid")))
            citation_count += trace["citation_guard"]["citation_count"]
            unsupported += trace["citation_guard"]["unsupported_count"]
            times.append((perf_counter() - start) * 1000)
            traces.append({"id": question.id, "status": "passed", **trace, "generation": usage, "latency_ms": times[-1]})
            rows.append(row)
        if mode == "decoder-smoke" and (not called or rows[0]["abstencion"]):
            raise DecoderFailure("DECODER_SMOKE_NO_GROUNDED_ANSWER", {"generation_called": bool(called), "abstention": rows[0]["abstencion"]})
        # Never publish partial final submissions or repair any model output.
        write_jsonl(directory / "submissions.jsonl", rows)
        record["submission_sha256"] = file_hash(directory / "submissions.jsonl")
        if mode == "sample":
            record["official_evaluation"] = run_eval(directory / "submissions.jsonl")
            write_json(directory / "evaluation.json", record["official_evaluation"])
        record["status"] = "passed"
    except Exception as exc:
        record["status"] = "failed"
        record["error"] = {"type": type(exc).__name__, "code": getattr(exc, "code", type(exc).__name__),
                           "detail": getattr(exc, "detail", {}), "message": str(exc)}
        if isinstance(exc, CitationGuardError):
            citation_count += exc.report["citation_count"]
            unsupported += exc.report["unsupported_count"]
            record["error"]["citation_guard"] = exc.report
    finally:
        if decoder is not None:
            record["assets"] = getattr(decoder, "assets", None)
            record["load_ms"] = getattr(decoder, "load_ms", None)
            try:
                record["memory"] = decoder._peak() if hasattr(decoder, "_peak") else {"peak_vram_bytes": None}
                decoder.close()
            except Exception as exc:
                record["cleanup_error"] = {"type": type(exc).__name__}
                record["status"] = "failed"
        total = perf_counter() - started
        ordered = sorted(times)
        input_tokens = sum(t["generation"].get("input_tokens", 0) for t in traces)
        output_tokens = sum(t["generation"].get("output_tokens", 0) for t in traces)
        generation_seconds = sum(t["generation"].get("generation_ms", 0) for t in traces) / 1000
        record["metrics"] = {"questions": len(inputs), "attempted": attempted, "completed": len(rows),
                             "model_generation_calls": called, "valid_json_rate": json_valid / attempted if attempted else None,
                             "citation_count": citation_count, "unsupported_citation_count": unsupported,
                             "unsupported_citation_rate": unsupported / citation_count if citation_count else 0.0,
                             "zero_citations_note": "Zero citations is not evidence of citation quality.",
                             "abstentions": sum(r["abstencion"] for r in rows),
                             "latency_p50_ms": statistics.median(times) if times else None,
                             "latency_p95_ms": ordered[max(0, (95 * len(ordered) + 99) // 100 - 1)] if ordered else None,
                             "input_tokens": input_tokens, "output_tokens": output_tokens,
                             "output_tokens_per_generation_second": output_tokens / generation_seconds if generation_seconds else None,
                             "completed_questions_per_second": len(rows) / total if total else None,
                             "total_seconds": total, "peak_vram_bytes": record.get("memory", {}).get("peak_vram_bytes"),
                             "errors": int(record["status"] == "failed"),
                             "oom_count": int(record.get("error", {}).get("code") == "CUDA_OOM")}
        packages = {}
        for name in ("torch", "transformers", "accelerate", "huggingface-hub", "bitsandbytes"):
            try:
                packages[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                packages[name] = None
        record["runtime"]["packages"] = packages
        write_jsonl(directory / "trace.jsonl", traces)
        write_json(directory / "experiment.json", record)
    return record
