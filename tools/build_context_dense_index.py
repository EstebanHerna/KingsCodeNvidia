"""Build a disposable Qwen dense index over structural metadata search text."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT
from kingscode.neural import build_context_dense


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=ROOT / "corpus")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/retrieval_context_v1")
    args = parser.parse_args(argv)
    report = build_context_dense(args.corpus, args.output)
    print(json.dumps({**report, "output": str(args.output)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
