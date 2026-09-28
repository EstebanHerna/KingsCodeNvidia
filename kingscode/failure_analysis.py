"""Retrieval failure analysis and taxonomy (Phase 5).

Consumes artifacts already produced by the evaluation boundary
(``reports/retrieval_*_per_question.jsonl`` and ``reports/legal_basis_audit.json``)
and classifies each evaluable question's retrieval outcome. It reads NO new
labels into retrieval: the gold targets were already extracted by
``evaluation.benchmark`` (the single label-reading layer) and are only reused
here for offline error analysis.

Failure taxonomy
----------------
- ``success``                   at least one gold target matched in the top-k.
- ``corpus_missing``            the gold target is not in the corpus at all
                                (coverage == 0), so retrieval could not succeed.
- ``correct_document_wrong_passage``  a passage from the right legal work was
                                retrieved, but not the right article/section.
- ``wrong_document``            the top result is from a different legal work and
                                no gold work appears in the top-k.
- ``ranking_failure``           a gold passage IS somewhere in the candidate
                                order but ranked out of the evaluated top-k.
- ``graph_failure``             a relation/hierarchy question where graph
                                expansion was expected to help but the gold
                                passage was reachable only through the graph and
                                still missed. Conservative: only asserted when a
                                relation signal is present.
- ``ambiguous_ground_truth``    the label is document-only, conflicting, or the
                                audit flagged it; no confident classification.

A failure is never forced when ``legal_basis`` is incomplete or contradictory:
those go to ``ambiguous_ground_truth``.

Metrics
-------
- ``document_mismatch_rate``: fraction of evaluable questions whose rank-1 result
  is from a document that is NOT any gold target document. This distinguishes
  wrong-document retrieval from wrong-passage retrieval. It is our own definition,
  NOT claimed to be identical to any academic Document Retrieval Mismatch metric.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import re

from .common import ROOT, read_json, read_jsonl, write_json

FAILURE_ANALYSIS_VERSION = "failure-analysis-v0.6"

_RELATION_SIGNAL = re.compile(
    r"\b(remisi[oó]n|remite|modific\w*|derog\w*|reglament\w*|concordan\w*|par[aá]grafo|inciso|deroga\w*)\b", re.I)


def _gold_docs(targets: list) -> set[tuple]:
    return {tuple(t[:3]) for t in targets}


def classify_question(pred: dict, audit: dict, question_text: str | None = None) -> dict:
    """Classify one evaluable question's retrieval outcome. Deterministic."""
    targets = [tuple(t) for t in audit.get("targets", [])]
    notes = audit.get("notes", [])
    coverage = audit.get("coverage")
    metrics = pred.get("metrics", {})
    retrieved = [tuple(t) for t in pred.get("retrieved_targets", [])]
    retrieved_docs = {t[:3] for t in retrieved}
    gold_docs = _gold_docs(targets)

    if not targets:
        return {"class": "ambiguous_ground_truth", "reason": "no_machine_extractable_target"}

    # An actual gold match is unambiguous evidence of success, even when the
    # label is otherwise noisy. Success is judged before ambiguity gates so a
    # partial-but-real hit is never miscounted as ambiguous.
    if metrics.get("legal_basis_any@10"):
        return {"class": "success", "reason": "gold_target_in_topk"}

    # From here the question failed. Only now do we protect against forcing a
    # failure class onto an incomplete or contradictory ground truth.
    if notes and any("conflict" in n.lower() or "only" in n.lower() or "unverified" in n.lower() for n in notes):
        return {"class": "ambiguous_ground_truth", "reason": "audit_flagged_label", "notes": notes}
    if all(t[3] is None for t in targets):
        return {"class": "ambiguous_ground_truth", "reason": "document_level_label_only"}

    # Distinguish the failure mode.
    if coverage == 0:
        return {"class": "corpus_missing", "reason": "no_gold_target_in_corpus"}

    covered_docs = {tuple(t[:3]) for t in audit.get("covered_targets", [])}
    if covered_docs and not (covered_docs & retrieved_docs):
        # Gold document exists in corpus and was covered, but retrieval brought
        # back none of the gold documents -> either wrong document or ranking.
        pass

    if gold_docs & retrieved_docs:
        # Right legal work retrieved, wrong article/section within it.
        return {"class": "correct_document_wrong_passage", "reason": "right_work_wrong_locator"}

    # Relation/hierarchy question where the graph was expected to help.
    if question_text and _RELATION_SIGNAL.search(question_text):
        if not pred.get("graph_active"):
            return {"class": "graph_failure", "reason": "relation_signal_graph_not_active"}
        return {"class": "graph_failure", "reason": "relation_signal_graph_active_still_missed"}

    if coverage and coverage > 0 and gold_docs and not (gold_docs & retrieved_docs):
        return {"class": "wrong_document", "reason": "topk_all_other_documents"}

    return {"class": "ranking_failure", "reason": "gold_covered_but_out_of_topk"}


def analyze(mode: str = "bm25", graph_mode: str = "off", *, rerank: bool = False) -> dict:
    """Build the failure-analysis report for one benchmark run/graph mode."""
    name = mode + ("_reranker" if rerank else "")
    predictions = read_jsonl(ROOT / f"reports/retrieval_{name}_per_question.jsonl")
    audit = {a["id"]: a for a in read_json(ROOT / "reports/legal_basis_audit.json")}
    sample = {r["id"]: r.get("pregunta") for r in read_jsonl(ROOT / "data/sample_50.jsonl")}
    rows = [p for p in predictions if p.get("graph_mode") == graph_mode]

    classified = []
    doc_mismatch_hits = 0
    doc_mismatch_evaluable = 0
    for p in rows:
        a = audit.get(p["id"], {})
        if not p.get("metrics", {}).get("evaluable"):
            continue
        result = classify_question(p, a, sample.get(p["id"]))
        classified.append({"id": p["id"], "area": p.get("area"), "format": p.get("format"),
                           "class": result["class"], "reason": result.get("reason"),
                           "coverage": p.get("coverage"),
                           "document_mismatch_at_1": bool(p.get("metrics", {}).get("document_mismatch@1"))})
        doc_mismatch_evaluable += 1
        if p.get("metrics", {}).get("document_mismatch@1"):
            doc_mismatch_hits += 1

    def counts(items):
        c: dict[str, int] = defaultdict(int)
        for it in items:
            c[it["class"]] += 1
        return dict(sorted(c.items()))

    by_area = defaultdict(list)
    by_format = defaultdict(list)
    for it in classified:
        by_area[it["area"]].append(it)
        by_format[it["format"]].append(it)

    return {"version": FAILURE_ANALYSIS_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "run": {"mode": mode, "rerank": rerank, "graph_mode": graph_mode},
            "taxonomy": ["success", "corpus_missing", "correct_document_wrong_passage",
                         "wrong_document", "ranking_failure", "graph_failure", "ambiguous_ground_truth"],
            "evaluable_questions": len(classified),
            "overall_counts": counts(classified),
            "by_area": {area: counts(items) for area, items in sorted(by_area.items())},
            "by_format": {fmt: counts(items) for fmt, items in sorted(by_format.items())},
            "document_mismatch_rate": {
                "value": doc_mismatch_hits / doc_mismatch_evaluable if doc_mismatch_evaluable else None,
                "hits": doc_mismatch_hits, "evaluable": doc_mismatch_evaluable,
                "definition": ("Fraction of evaluable questions whose rank-1 passage belongs to a "
                               "document that is not any gold-target document. Own definition; not "
                               "claimed identical to any academic DRM metric."),
            },
            "per_question": sorted(classified, key=lambda r: r["id"]),
            "caveats": ["legal_basis is a noisy proxy; ambiguous/contradictory labels are not forced into a failure class.",
                        "Classification is offline error analysis, not an official QA score."]}


def build_report(mode: str = "bm25", graph_mode: str = "off", *, rerank: bool = False) -> dict:
    report = analyze(mode, graph_mode, rerank=rerank)
    suffix = f"{mode}{'_reranker' if rerank else ''}_{graph_mode}"
    write_json(ROOT / f"reports/retrieval_failures_{suffix}.json", report)
    return report
