"""Build/check the source-extractive pilot, or run DEV on CPU. No holdout CLI."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT
from kingscode.benchmark_v2 import build, check, evaluate_dev

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["build", "check", "dev"])
    p.add_argument("--corpus", type=Path, default=ROOT / "corpus")
    args = p.parse_args()
    if args.command == "build": result = build(args.corpus)
    elif args.command == "check": result = check()
    else:
        from kingscode.retrieval import Retriever
        retriever = Retriever(args.corpus, exact_locator=True, graph_budget=0)
        result = evaluate_dev(retriever.retrieve, args.corpus, output=ROOT / "reports/member_a_v02/benchmark_v2_dev.json")
    print(json.dumps(result, ensure_ascii=False, indent=2))
