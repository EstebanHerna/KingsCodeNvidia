"""Run one retrieval variable at a time, then freeze selected exact evidence."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, read_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    run = sub.add_parser("run")
    run.add_argument("--candidate", required=True, choices=[f"R{i}" for i in range(6)])
    run.add_argument("--output-root", type=Path, default=ROOT / "reports/retrieval_matrix")
    freeze = sub.add_parser("freeze")
    freeze.add_argument("--run", type=Path, required=True)
    freeze.add_argument("--output", type=Path, default=ROOT / "artifacts/retrieval_freeze.json")
    args = parser.parse_args(argv)
    if args.command == "list":
        result = read_json(ROOT / "config/experiment_matrix.json")
    else:
        from kingscode.generation.retrieval_experiments import run_retrieval, freeze_retrieval
        result = (run_retrieval(args.candidate, output_root=args.output_root) if args.command == "run"
                  else freeze_retrieval(args.run, args.output))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(result.get("status") == "failed")


if __name__ == "__main__":
    raise SystemExit(main())
