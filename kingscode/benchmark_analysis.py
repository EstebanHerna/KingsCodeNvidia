"""Post-ranking comparison and error analysis for the internal IR benchmark."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .common import ROOT, file_hash, read_json, read_jsonl, write_json
from .retrieval_benchmark import benchmark_identity, bootstrap_reports, complementarity

ACTIONS = {
    "corpus_missing": {"owner": "BENCHMARK CURATOR", "action": "verify gold/source coverage; investigate acquisition only with evidence"},
    "wrong_document": {"owner": "RETRIEVAL EXPERIMENTER", "action": "inspect canonical identity, document-level metadata, and document-first retrieval"},
    "correct_document_wrong_passage": {"owner": "RETRIEVAL EXPERIMENTER", "action": "inspect locator matching, chunk boundaries, and near-top ranking"},
    "ranking_failure": {"owner": "RETRIEVAL EXPERIMENTER", "action": "inspect dense/hybrid/reranker once GPU prerequisites exist"},
    "graph_failure": {"owner": "RETRIEVAL EXPERIMENTER", "action": "inspect graph seeding/router/traversal using evidenced relations"},
    "ambiguous_gold": {"owner": "BENCHMARK CURATOR", "action": "fix annotation; do not change retrieval"},
}


def load_run(directory: Path) -> tuple[dict, list[dict]]:
    report = read_json(directory / "report.json")
    rows = read_jsonl(directory / "per_question.jsonl")
    if report.get("status") != "passed":
        raise ValueError("Only passed runs can be analyzed")
    if report.get("per_question_sha256") != file_hash(directory / "per_question.jsonl"):
        raise ValueError("Per-question artifact hash mismatch")
    return report, rows


def compare(baseline_dir: Path, candidate_dir: Path) -> dict:
    baseline, base_rows = load_run(baseline_dir)
    candidate, candidate_rows = load_run(candidate_dir)
    if baseline["benchmark"]["manifest_sha256"] != candidate["benchmark"]["manifest_sha256"]:
        raise ValueError("Cannot compare runs from different benchmark manifests")
    if baseline["split"] != candidate["split"]:
        raise ValueError("Cannot compare runs from different splits")
    return {"version": "benchmark-comparison-v1", "benchmark": benchmark_identity(),
            "baseline": {"variant": baseline["variant"], "directory": baseline["directory"], "metrics": baseline["metrics"]},
            "candidate": {"variant": candidate["variant"], "directory": candidate["directory"], "metrics": candidate["metrics"]},
            "bootstrap": bootstrap_reports(base_rows, candidate_rows),
            "note": "If a confidence interval includes zero, the paired difference is inconclusive."}


def error_analysis(directory: Path) -> dict:
    report, rows = load_run(directory)
    by_class, by_area, by_tag, examples = Counter(), defaultdict(Counter), defaultdict(Counter), defaultdict(list)
    for row in rows:
        failure = row["failure"]
        if failure == "success":
            continue
        # The benchmark's generated exact gold has already been corpus-verified.
        # A miss is a retrieval failure; ambiguous-gold is reserved for later
        # human-authored cases and never fabricated here.
        mapped = failure
        by_class[mapped] += 1
        by_area[row["question"]["area"]][mapped] += 1
        for tag in row["question"]["tags"]:
            by_tag[tag][mapped] += 1
        if len(examples[mapped]) < 10:
            examples[mapped].append({"id": row["id"], "question": row["question"]["question"],
                                     "area": row["question"]["area"], "tags": row["question"]["tags"],
                                     "retrieved": row["retrieved"][:3], "recommendation": ACTIONS.get(mapped)})
    return {"version": "benchmark-error-analysis-v1", "benchmark": benchmark_identity(),
            "run": {"variant": report["variant"], "split": report["split"], "directory": report["directory"]},
            "counts": dict(sorted(by_class.items())),
            "by_area": {area: dict(sorted(c.items())) for area, c in sorted(by_area.items())},
            "by_tag": {tag: dict(sorted(c.items())) for tag, c in sorted(by_tag.items())},
            "representative_cases": dict(examples), "owner_action": ACTIONS,
            "policy": "Failures drive targeted investigation; no blind corpus expansion."}


def write_comparison(baseline_dir: Path, candidate_dir: Path, output: Path) -> dict:
    result = compare(baseline_dir, candidate_dir)
    write_json(output, result)
    return result


def write_error_analysis(directory: Path, output: Path) -> dict:
    result = error_analysis(directory)
    write_json(output, result)
    return result


def write_complementarity_status(output: Path) -> dict:
    result = {"version": "benchmark-complementarity-status-v1", "benchmark": benchmark_identity(),
              "status": "GPU_BLOCKED", "executed_pairs": [],
              "user_reported_bge_m3_old_official_sample": {"Recall@5": 0.4100, "Recall@10": 0.4593,
                  "verification": "No underlying report/config/index exists in this repository; retained as user-reported only, not reproduced evidence."},
              "required_pairs": ["BM25 vs BGE-M3", "BM25 vs Qwen3-Embedding-0.6B"],
              "required_outputs": ["both_hit", "bm25_only", "dense_only", "both_miss", "intersection", "union", "oracle_union_recall", "examples"],
              "blockers": ["local CPU-only environment", "Qwen dense index absent", "BGE-M3 lacks approved immutable model lock and local loader/index implementation"],
              "next_step": "On approved GPU, run same-ID dense variants then call kingscode.retrieval_benchmark.complementarity at k=1,3,5,8,10."}
    write_json(output, result)
    return result
