"""Immutable per-run artifacts plus stable, content-derived experiment identity."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
from time import perf_counter

from ..common import ROOT, file_hash, read_json, write_json, write_jsonl
from .contracts import load_questions
from .decoder import GENERATION_CONFIG, PROMPT_VERSION, DummyDecoder
from .evaluation import official_hashes, run_eval
from .guards import CitationGuardError, GUARD_VERSION, SubmissionValidationError
from .pipeline import Pipeline
from .policy import POLICY_VERSION
from .query import QUERY_VERSION
from .routing import ROUTER_VERSION, RetrieverGraphRouter


def fingerprint(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def validate_config(config: dict) -> None:
    r = config["retrieval"]
    if r["mode"] != "bm25" or r["rerank"] is not False or config["decoder_backend"] != "dummy_abstain":
        raise ValueError("Gate 1B only allows BM25 and the offline dummy; no model loading")
    if config["generation"] != GENERATION_CONFIG or config["evaluation"] != {"split": "sample", "ragas": False}:
        raise ValueError("Gate 1B generation/evaluation must be deterministic and offline")
    if type(r["candidate_k"]) is not int or r["candidate_k"] < 1 or type(r["graph_budget"]) is not int or r["graph_budget"] < 0:
        raise ValueError("Invalid retrieval configuration")
    if type(r["k"]) is not int or not 1 <= r["k"] <= 10 or config["graph_policy"] not in {"router", "off", "auto", "on"}:
        raise ValueError("Invalid k or graph policy")


def run_experiment(*, config_path: Path = ROOT / "config/reasoning.json", output_root: Path = ROOT / "reports/member_b",
                   corpus_dir: Path = ROOT / "corpus", questions_path: Path = ROOT / "data/sample_50.jsonl",
                   retrieve=None, decoder=None) -> dict:
    config = read_json(config_path)
    validate_config(config)
    official = official_hashes()
    questions = load_questions(questions_path)
    public = [q.public_record() for q in questions]
    manifest = read_json(corpus_dir / "manifest.json")
    backend = decoder or DummyDecoder()
    identity = {
        "version": config["version"], "public_questions_sha256": fingerprint(public),
        "corpus": {"version": manifest["version"], "passages_sha256": manifest["hashes"]["passages.jsonl"],
                   "manifest_sha256": file_hash(corpus_dir / "manifest.json")},
        "graph": {"version": manifest["parser_version"], "nodes_sha256": manifest["hashes"]["graph/nodes.jsonl"],
                  "edges_sha256": manifest["hashes"]["graph/edges.jsonl"]},
        "retrieval_config": config["retrieval"], "graph_policy": config["graph_policy"], "router_version": ROUTER_VERSION,
        "query_version": QUERY_VERSION, "guard_version": GUARD_VERSION, "abstention_policy_version": POLICY_VERSION,
        "decoder_backend": {"name": backend.name, "version": backend.version}, "prompt_version": PROMPT_VERSION,
        "generation_config": config["generation"], "evaluation_config": config["evaluation"],
        "official_hashes": official,
        "implementation_sha256": {p.relative_to(ROOT).as_posix(): file_hash(p) for p in sorted((ROOT / "kingscode/reasoning").glob("*.py"))},
    }
    identity_hash = fingerprint(identity)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = output_root.resolve() / f"{stamp}-{identity_hash[:12]}"
    run_dir.mkdir(parents=True, exist_ok=False)
    write_jsonl(run_dir / "questions.jsonl", public)
    record = {"fingerprint": identity_hash, "identity": identity, "timestamp": stamp, "status": "running",
              "paths": {"run": str(run_dir), "submission": str(run_dir / "submissions.jsonl"),
                        "trace": str(run_dir / "trace.jsonl"), "evaluation": str(run_dir / "evaluation.json")},
              "runtime": {"python": sys.version, "platform": platform.platform()},
              "settings": {"config_path": str(config_path.resolve()), "corpus_dir": str(corpus_dir.resolve()),
                           "questions_path": str(questions_path.resolve())}, "official_evaluation": None,
              "limitation": "Dummy abstains on every item. No legal reasoning quality, real decoder, GPU or RAGAS claim."}
    rows, traces = [], []
    attempts, rejected_citations, rejected_schema, citation_count, unsupported_count = 0, 0, 0, 0, 0
    started = perf_counter()
    error = None
    try:
        adapter = RetrieverGraphRouter()
        if retrieve is None:
            # Only constructor and public retrieve method: no BM25/graph internals.
            from kingscode import Retriever
            r = config["retrieval"]
            retriever = Retriever(corpus_dir, mode=r["mode"], rerank=r["rerank"], graph_router=adapter,
                                  candidate_k=r["candidate_k"], graph_budget=r["graph_budget"])
            retrieve = retriever.retrieve
        pipeline = Pipeline(retrieve, adapter=adapter, decoder=backend, k=config["retrieval"]["k"], graph_policy=config["graph_policy"])
        initialized = perf_counter()
        for question in questions:
            attempts += 1
            row, trace = pipeline.run(question)
            rows.append(row)
            traces.append(trace)
            citation_count += trace["citation_guard"]["citation_count"]
            unsupported_count += trace["citation_guard"]["unsupported_count"]
        # Publish a final JSONL only after every row passes both blocking gates.
        write_jsonl(run_dir / "submissions.jsonl", rows)
        write_jsonl(run_dir / "trace.jsonl", traces)
        record["official_evaluation"] = run_eval(run_dir / "submissions.jsonl")
        write_json(run_dir / "evaluation.json", record["official_evaluation"])
        record["submission_sha256"] = file_hash(run_dir / "submissions.jsonl")
        record["initialization_ms"] = (initialized - started) * 1000
        record["status"] = "passed"
    except Exception as exc:
        error = exc
        record["status"] = "failed"
        record["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        if isinstance(exc, CitationGuardError):
            rejected_citations = 1
            citation_count += exc.report["citation_count"]
            unsupported_count += exc.report["unsupported_count"]
            record["failure"]["guard"] = exc.report
        if isinstance(exc, SubmissionValidationError):
            rejected_schema = 1
    finally:
        times = sorted(t["latency_ms"] for t in traces)
        record["metrics"] = {
            "questions": len(questions), "attempted": attempts, "completed": len(rows),
            "valid_json_rate": (len(rows) + rejected_citations) / attempts if attempts else None,
            "schema_rejections": rejected_schema, "citation_rejections": rejected_citations,
            "citation_count": citation_count, "unsupported_citation_count": unsupported_count,
            "unsupported_citation_rate": unsupported_count / citation_count if citation_count else 0.0,
            "citation_rate_note": "Zero with zero citations is vacuous, not evidence of citation quality.",
            "abstentions": sum(r["abstencion"] for r in rows),
            "abstention_reasons": dict(Counter(t["abstention_reason"] for t in traces)),
            "graph_decisions": dict(Counter(t["graph_decision"] for t in traces)),
            "latency_p50_ms": statistics.median(times) if times else None,
            "latency_p95_ms": times[max(0, (95 * len(times) + 99) // 100 - 1)] if times else None,
            "total_seconds": perf_counter() - started,
        }
        record["neural_modules_loaded"] = sorted(m for m in ("torch", "transformers", "kingscode.neural") if m in sys.modules)
        write_json(run_dir / "experiment.json", record)
    if error is not None:
        raise RuntimeError(f"Experiment failed; see {run_dir / 'experiment.json'}") from error
    return record
