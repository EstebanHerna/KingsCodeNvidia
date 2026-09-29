"""Command line entry point for the member A knowledge layer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["acquire", "build", "benchmark", "verify", "query", "dense",
                                            "reproduce", "backlog", "coverage", "failures", "experiment"])
    parser.add_argument("--experiment-name", choices=["R6", "R7", "R8"], default="R6")
    parser.add_argument("--corpus", type=Path, default=ROOT / "corpus")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--question")
    parser.add_argument("--k", type=int, default=8)
    parser.add_argument("--graph-mode", choices=["off", "auto", "on"], default="auto")
    parser.add_argument("--mode", choices=["bm25", "dense", "hybrid"], default="bm25")
    parser.add_argument("--rerank", action="store_true")
    parser.add_argument("--exact-locator", action="store_true", help="Add exact legal candidates before reranking")
    args = parser.parse_args()
    if args.command == "acquire":
        from kingscode.acquisition import acquire
        result = acquire(args.corpus, args.limit, args.workers)
        print(json.dumps({"targets": result["targets"], "downloaded": result["downloaded"],
                          "failed": [{"doc_id": d["doc_id"], "error": d["error"]}
                                     for d in result["documents"] if d["status"] != "downloaded"]}, ensure_ascii=False, indent=2))
    elif args.command in {"build", "reproduce"}:
        from kingscode.corpus import build
        print(json.dumps(build(args.corpus), ensure_ascii=False, indent=2))
        if args.command == "reproduce":
            from kingscode.evaluation import benchmark
            from kingscode.validation import verify
            print(json.dumps(benchmark(args.corpus), ensure_ascii=False, indent=2))
            print(json.dumps(verify(args.corpus), ensure_ascii=False, indent=2))
    elif args.command == "query":
        from kingscode.retrieval import Retriever
        if not args.question:
            parser.error("--question required")
        print(json.dumps(Retriever(args.corpus, mode=args.mode, rerank=args.rerank, exact_locator=args.exact_locator).retrieve(
            args.question, args.k, args.graph_mode), ensure_ascii=False, indent=2))
    elif args.command == "benchmark":
        from kingscode.evaluation import benchmark
        print(json.dumps(benchmark(args.corpus, mode=args.mode, rerank=args.rerank), ensure_ascii=False, indent=2))
    elif args.command == "verify":
        from kingscode.validation import verify
        print(json.dumps(verify(args.corpus), ensure_ascii=False, indent=2))
    elif args.command == "backlog":
        from kingscode.acquisition_backlog import build_report
        r = build_report(args.corpus)
        print(json.dumps({"total_unresolved": r["total_unresolved"], "counts": r["counts"]},
                         ensure_ascii=False, indent=2))
    elif args.command == "coverage":
        from kingscode.coverage_report import build_report
        r = build_report(args.corpus)
        print(json.dumps({"totals": r["totals"], "unresolved": r["unresolved_acquisition_targets"],
                          "duplicates": r["duplicates_detected"]}, ensure_ascii=False, indent=2))
    elif args.command == "failures":
        from kingscode.failure_analysis import build_report
        r = build_report(args.mode, args.graph_mode, rerank=args.rerank)
        print(json.dumps({"overall_counts": r["overall_counts"],
                          "document_mismatch_rate": r["document_mismatch_rate"]}, ensure_ascii=False, indent=2))
    elif args.command == "experiment":
        from kingscode.retrieval import Retriever
        from kingscode.metadata_experiments import run_experiment
        if not args.question:
            parser.error("--question required")
        retriever = Retriever(args.corpus, mode=args.mode, rerank=args.rerank)
        print(json.dumps(run_experiment(args.experiment_name, retriever, args.question, args.k),
                         ensure_ascii=False, indent=2))
    else:
        from kingscode.neural import build_dense
        print(json.dumps(build_dense(args.corpus), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
