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
    parser.add_argument("command", choices=["smoke", "decoder-smoke", "sample", "bakeoff"])
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


if __name__ == "__main__":
    raise SystemExit(main())
