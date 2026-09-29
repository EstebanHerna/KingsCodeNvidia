"""Planner diagnostics: R_BASE (Q0) vs R_PLAN (Q0 + Q1..Q3) on A's retrieval benchmark.

Measurement only, never part of the competitive pipeline. Same retrieval for both
arms (graph OFF, same k, same corpus/index); the only variable is the planner
views, replayed from a frozen plans directory. Rankings are computed and written
before any gold file is read (A's benchmark rule). Holdout is refused.

  python tools/analyze_query_plans.py --plans reports/query_plans/<id> --split dev

Outputs reports/query_plans/<id>/diagnostics_<split>.json with:
  BASE_ONLY / PLAN_ONLY / BOTH / NEITHER (complete gold evidence in top-k)
  Oracle Multi-View Recall  union of Q0..Q3 (depth each) holds the complete gold
  Planner Miss Rate         union lacks the gold          -> query/representation failure
  Fusion Loss               union has it, fused top-k not -> fusion/ranking failure
  Preservation Rate         Q0 dates/amounts/negations kept by the planner
  Unsupported Hypothesis    generated references absent from all retrieved evidence
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kingscode.common import read_jsonl, write_json  # noqa: E402
from kingscode.reasoning.official import official_bodies  # noqa: E402
from kingscode.reasoning.pipeline import locator_switch, rrf_merge, supports_query_views  # noqa: E402
from kingscode.reasoning.plan_store import PlanStore  # noqa: E402

BENCH = ROOT / "benchmarks/kingscode_ir"


def _call(retrieve, switch, text, k, trusted):
    return retrieve(text, k, "off", **({switch: False} if switch and not trusted else {}))


def rankings(items, store, retrieve, *, k=8, depth=32) -> list[dict]:
    """R_PLAN uses exactly the production path: A's native query_views when available."""
    switch, native = locator_switch(retrieve), supports_query_views(retrieve)
    out = []
    for qid, text in items:
        plan = store.get(qid, text)
        base = _call(retrieve, switch, text, k, True)
        if plan.views and native:
            fused = retrieve(text, k, "off", query_views=list(plan.views))
        elif plan.views:
            fused = rrf_merge([base, *[_call(retrieve, switch, v, k, False) for v in plan.views]], k)
        else:
            fused = base
        union = [_call(retrieve, switch, text, depth, True)] + [_call(retrieve, switch, v, depth, False) for v in plan.views]
        out.append({"id": qid, "plan_status": plan.status, "views": list(plan.views),
                    "generated_references": list(plan.generated_references),
                    "preservation_rate": plan.preservation.get("rate"),
                    "base": base, "plan": fused, "union": [p for lst in union for p in lst]})
    return out


def _fragment(passage) -> str | None:
    if passage.get("canonical_fragment_id"):
        return passage["canonical_fragment_id"]
    try:
        from kingscode.metadata import canonical_fragment_id
        return canonical_fragment_id(passage)
    except Exception:
        return None


def _covered(passages, gold) -> bool:
    """Complete gold evidence: every gold fragment present (by id or by its gold span passage)."""
    frags = {_fragment(p) for p in passages}
    pids = {p["passage_id"] for p in passages}
    return all(f in frags or bool(gold["span_passages"].get(f, set()) & pids) for f in gold["fragments"])


def _ref_body(ref) -> tuple:
    return tuple(ref[0]) if isinstance(ref[0], (tuple, list)) else tuple(ref[:3])


def load_gold(path: Path) -> dict:
    gold = {}
    for record in read_jsonl(path):
        spans = {}
        for span in record.get("gold_spans", []):
            spans.setdefault(span["canonical_fragment_id"], set()).add(span["passage_id"])
        gold[record["id"]] = {"fragments": list(record["gold_fragment_ids"]), "span_passages": spans}
    return gold


def diagnose(ranked: list[dict], gold: dict) -> dict:
    from kingscode.retrieval_benchmark import paired_bootstrap
    cats = {"BASE_ONLY": 0, "PLAN_ONLY": 0, "BOTH": 0, "NEITHER": 0}
    base_v, plan_v, oracle, miss, loss, gen, unsupported, rates, per = [], [], 0, 0, 0, 0, 0, [], []
    for r in ranked:
        g = gold[r["id"]]
        b, p, u = _covered(r["base"], g), _covered(r["plan"], g), _covered(r["union"], g)
        cats["BOTH" if b and p else "BASE_ONLY" if b else "PLAN_ONLY" if p else "NEITHER"] += 1
        base_v.append(float(b))
        plan_v.append(float(p))
        oracle += u
        miss += not u
        loss += u and not p
        evidence = set()
        for passage in r["union"]:
            evidence |= official_bodies(passage.get("text", ""))
        for ref in r["generated_references"]:
            gen += 1
            unsupported += _ref_body(ref) not in evidence
        if r["preservation_rate"] is not None:
            rates.append(r["preservation_rate"])
        per.append({"id": r["id"], "base": b, "plan": p, "union": u, "plan_status": r["plan_status"]})
    n = len(ranked)
    return {"questions": n, "categories": cats,
            "evidence_completeness": {"base": sum(base_v) / n, "plan": sum(plan_v) / n},
            "bootstrap_plan_minus_base": paired_bootstrap(base_v, plan_v),
            "oracle_multi_view_recall": oracle / n, "planner_miss_rate": miss / n, "fusion_loss": loss / n,
            "preservation_rate": (sum(rates) / len(rates)) if rates else None,
            "generated_references": gen,
            "unsupported_hypothesis_rate": (unsupported / gen) if gen else None,
            "per_question": per}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plans", type=Path, required=True)
    ap.add_argument("--split", choices=["dev", "validation"], default="dev")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--depth", type=int, default=32)
    ap.add_argument("--corpus", type=Path, default=ROOT / "corpus")
    args = ap.parse_args()
    from kingscode import Retriever
    items = [(q["id"], q["question"]) for q in read_jsonl(BENCH / "questions" / f"{args.split}.jsonl")]
    store = PlanStore(args.plans)
    ranked = rankings(items, store, Retriever(args.corpus).retrieve, k=args.k, depth=args.depth)
    write_json(args.plans / f"rankings_{args.split}.json",
               [{**r, "generated_references": [list(map(str, x)) for x in r["generated_references"]],
                 **{k: [p["passage_id"] for p in r[k]] for k in ("base", "plan", "union")}} for r in ranked])
    report = diagnose(ranked, load_gold(BENCH / "gold" / f"{args.split}.jsonl"))  # gold only after rankings
    report["claim"] = "INTERNAL BENCHMARK ONLY; v1 is 100% EXPLICIT: no generalization claim to semantic questions."
    write_json(args.plans / f"diagnostics_{args.split}.json", report)
    print(json.dumps({k: v for k, v in report.items() if k != "per_question"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
