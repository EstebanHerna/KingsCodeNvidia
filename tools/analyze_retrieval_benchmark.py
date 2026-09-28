"""Create paired-bootstrap comparisons, error analysis, or complementarity status."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.benchmark_analysis import write_comparison, write_complementarity_status, write_error_analysis
from kingscode.common import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["compare", "errors", "complementarity-status"])
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "compare":
        if not args.baseline or not args.candidate:
            parser.error("compare requires --baseline and --candidate")
        result = write_comparison(args.baseline, args.candidate, args.output)
    elif args.command == "errors":
        if not args.run:
            parser.error("errors requires --run")
        result = write_error_analysis(args.run, args.output)
    else:
        result = write_complementarity_status(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
