"""Build or validate the deterministic KingsCode internal retrieval benchmark."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT
from kingscode.benchmark_builder import build, verify


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=ROOT / "corpus")
    parser.add_argument("--cases-per-area", type=int, choices=[10, 20], default=20)
    parser.add_argument("--check", action="store_true", help="Validate existing artifacts without rewriting them")
    args = parser.parse_args()
    result = verify(args.corpus) if args.check else build(args.corpus, cases_per_area=args.cases_per_area)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
