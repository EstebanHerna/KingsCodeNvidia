"""Preserved Gate 1B smoke plus explicit, separate Gate 2 decoder commands."""
from pathlib import Path
import argparse
import json
import os
import sys
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT
from kingscode.reasoning.experiments import run_experiment


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["smoke", "decoder-smoke", "sample", "bakeoff", "batch", "verify", "plan"])
    parser.add_argument("--input", type=Path, help="batch/verify/plan: questions JSONL (public fields only are read)")
    parser.add_argument("--run-dir", type=Path, help="batch: checkpoint/output directory")
    parser.add_argument("--fresh", action="store_true", help="batch: refuse to resume an existing run directory")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retrieval-mode", choices=["base", "option", "plan"], default="option")
    parser.add_argument("--plans", type=Path, help="plan mode: frozen reports/query_plans/<id> directory (replay)")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--graph-policy", choices=["router", "off", "auto", "on"], default="router")
    parser.add_argument("--synthetic", type=int, help="batch: rehearsal with the input repeated to N questions with new ids")
    parser.add_argument("--delivered", type=Path, help="verify: submissions.jsonl to compare against")
    parser.add_argument("--only", help="verify: comma-separated ids to regenerate")
    parser.add_argument("--exact-locator", action="store_true", help="A's exact locator (resolves only the original question)")
    parser.add_argument("--retriever-mode", choices=["bm25", "dense", "hybrid"], default="bm25")
    parser.add_argument("--rerank", action="store_true")
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--retrieval-freeze", type=Path)
    parser.add_argument("--precision", choices=["bf16", "int8", "int4"], default="bf16")
    parser.add_argument("--oom-record", type=Path)
    parser.add_argument("--allow-optional", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan only; no CUDA, weights or evaluation")
    args = parser.parse_args(argv)
    if args.command == "smoke":
        if args.model or args.precision != "bf16" or args.oom_record or args.retrieval_freeze or args.allow_optional or args.dry_run:
            parser.error("smoke retains the exact Gate 1B dummy contract; use only --config/--output-root")
        result = run_experiment(config_path=args.config or ROOT / "config/reasoning.json",
                                output_root=args.output_root or ROOT / "reports/member_b")
        print(json.dumps({"status": result["status"], "fingerprint": result["fingerprint"], "paths": result["paths"],
                      "submission_sha256": result["submission_sha256"], "metrics": result["metrics"],
                      "official_total": result["official_evaluation"]["total_automatico"],
                      "neural_modules_loaded": result["neural_modules_loaded"]}, ensure_ascii=False, indent=2))
        return 0
    if args.command in {"batch", "verify", "plan"}:
        return run_b_command(args, parser)
    from kingscode.generation.config import load_bakeoff, select_decoder
    config_path = args.config or ROOT / "config/decoder_bakeoff.json"
    cfg = load_bakeoff(config_path)
    if args.command != "bakeoff" and not args.model:
        parser.error("--model is required")
    if args.command == "bakeoff" and (args.model or args.precision != "bf16" or args.oom_record):
        parser.error("bakeoff varies only decoder in BF16; run precision fallbacks as separate sample experiments")
    models = ([args.model] if args.model else [name for name, c in cfg["candidates"].items() if c["enabled"] or args.allow_optional])
    selected = {name: select_decoder(name, cfg, allow_optional=args.allow_optional) for name in models}
    freeze = args.retrieval_freeze or ROOT / cfg["retrieval_freeze"]
    if args.dry_run:
        print(json.dumps({"status": "prepared_not_executed", "command": args.command, "candidates": selected,
                          "retrieval_freeze": str(freeze), "precision": args.precision,
                          "prompt_version": cfg["prompt_version"], "generation": cfg["generation"],
                          "gpu_validated": False}, ensure_ascii=False, indent=2))
        return 0
    output_root = args.output_root or ROOT / "reports/decoders"
    if args.command != "bakeoff":
        from kingscode.generation.experiments import run_generation
        result = run_generation(args.model, mode=args.command, config_path=config_path, freeze_path=freeze,
                                output_root=output_root, precision=args.precision, oom_record=args.oom_record,
                                allow_optional=args.allow_optional)
        print(json.dumps({k: result.get(k) for k in ("status", "paths", "metrics", "error", "official_evaluation")}, ensure_ascii=False, indent=2))
        return int(result["status"] != "passed")
    # New process per decoder: retrieval evidence stays fixed, VRAM is released.
    from kingscode.common import file_hash, write_json
    from kingscode.generation.retrieval_experiments import load_freeze
    load_freeze(freeze)
    freeze_hash = file_hash(freeze)
    results = []
    for name in models:
        if file_hash(freeze) != freeze_hash:
            raise ValueError("Frozen evidence changed during bakeoff")
        command = [sys.executable, str(Path(__file__).resolve()), "sample", "--model", name,
                   "--config", str(config_path), "--retrieval-freeze", str(freeze), "--output-root", str(output_root)]
        if args.allow_optional:
            command.append("--allow-optional")
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        try:
            result = json.loads(proc.stdout)
        except ValueError:
            result = {"status": "failed", "error": {"code": "CHILD_PROCESS_FAILED", "returncode": proc.returncode}}
        results.append({"model": name, "returncode": proc.returncode, **result})
    report = {"status": "passed" if all(r["status"] == "passed" and r["returncode"] == 0 for r in results) else "failed",
              "retrieval_freeze_sha256": freeze_hash, "precision": "bf16", "results": results}
    path = output_root / ("bakeoff-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    write_json(path, report)
    print(json.dumps({"report": str(path), **report}, ensure_ascii=False, indent=2))
    return int(report["status"] != "passed")


def _read_items(path: Path) -> list[tuple]:
    """(id, question text) only: the planner never sees options, labels or gold."""
    items = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            record = json.loads(line)
            items.append((record["id"], record.get("pregunta", record.get("question"))))
    return items


def _pipeline(args):
    from kingscode import Retriever
    from kingscode.reasoning import DummyDecoder, Pipeline, RetrieverGraphRouter
    from kingscode.reasoning.plan_store import PlanStore
    adapter = RetrieverGraphRouter()
    retriever = Retriever(args.corpus, mode=args.retriever_mode, rerank=args.rerank, graph_router=adapter,
                          exact_locator=args.exact_locator)
    decoder = DummyDecoder()
    if args.model:
        from kingscode.generation.hf_decoder import HFDecoder
        decoder = HFDecoder(args.model, precision=args.precision, allow_optional=args.allow_optional)
    plans = PlanStore(args.plans) if args.plans else None
    identity = {"decoder": [decoder.name, decoder.version], "retrieval_mode": args.retrieval_mode, "k": args.k,
                "retriever": {"mode": args.retriever_mode, "rerank": args.rerank, "exact_locator": args.exact_locator,
                              "corpus_sha256": retriever.corpus_hash},
                "graph_policy": args.graph_policy, "plans": plans.manifest["experiment_id"] if plans else None}
    return Pipeline(retriever.retrieve, adapter=adapter, decoder=decoder, k=args.k, graph_policy=args.graph_policy,
                    retrieval_mode=args.retrieval_mode, plans=plans), identity


def run_b_command(args, parser) -> int:
    from kingscode.reasoning.contracts import load_questions
    source = args.input or ROOT / "data/sample_50.jsonl"
    if args.command == "plan":
        from kingscode.reasoning.planner import PLANNER_PROMPT_VERSION, prompt_sha256
        items = _read_items(source)
        if args.dry_run:
            print(json.dumps({"status": "prepared_not_executed", "questions": len(items), "model": args.model or "qwen3-8b",
                              "prompt_version": PLANNER_PROMPT_VERSION, "prompt_sha256": prompt_sha256()}, indent=2))
            return 0
        from kingscode.generation.planner_backend import QwenPlannerBackend
        from kingscode.reasoning.plan_store import freeze_plans
        out = freeze_plans(items, QwenPlannerBackend(args.model or "qwen3-8b", precision=args.precision))
        print(json.dumps({"plans": str(out), **json.loads((out / "manifest.json").read_text(encoding="utf-8"))["counts"]}, indent=2))
        return 0
    questions = load_questions(source)
    pipeline, identity = _pipeline(args)
    if args.command == "verify":
        from kingscode.reasoning.batch import verify_items
        if not args.delivered or not args.only:
            parser.error("verify needs --delivered and --only")
        report = verify_items(pipeline, questions, args.delivered, [int(x) for x in args.only.split(",")])
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return int(not report["all_match"])
    from kingscode.reasoning.batch import BatchRunner, synthetic_questions
    if not args.run_dir:
        parser.error("batch needs --run-dir")
    if args.synthetic:
        questions = synthetic_questions(questions, args.synthetic)
    report = BatchRunner(pipeline, args.run_dir, identity=identity, retries=args.retries).run(questions, resume=not args.fresh)
    print(json.dumps({k: report[k] for k in ("submission", "rows", "complete", "fallback_ids", "submission_sha256", "counts", "seconds")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
