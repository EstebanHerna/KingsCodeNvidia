"""Validate KC-COL-IR v0.1 provenance, family splits and deterministic sampling."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks/kc_col_ir_v0.1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify() -> dict:
    manifest = json.loads((BENCH / "manifest.json").read_text(encoding="utf-8"))
    sources = read_jsonl(BENCH / "source_manifest.jsonl")
    questions = read_jsonl(BENCH / "questions/dev.jsonl")
    gold = read_jsonl(BENCH / "gold/dev.jsonl")
    sample = json.loads((BENCH / "sampling_manifest.json").read_text(encoding="utf-8"))
    required = {"source_id", "institution", "institution_family", "title", "year", "source_type",
                "official_url", "final_url", "host", "sha256", "bytes_verified", "question_count",
                "question_format", "answer_key_available", "area", "intended_role", "split",
                "access_status", "copyright_status", "exposure_status"}
    if any(required - row.keys() for row in sources):
        raise ValueError("Source manifest has missing contract fields")
    ids = [row["source_id"] for row in sources]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate source_id")
    allowed_types = {"INSTITUTIONAL_QUESTION_BANK", "INSTITUTIONAL_ASSESSMENT", "OFFICIAL_EXAM",
                     "TOPIC_GUIDE", "METHODOLOGY_GUIDE"}
    if any(row["source_type"] not in allowed_types for row in sources):
        raise ValueError("Unknown source type")
    if any(row["institution_family"] == "universidad_libre_preparatorios" and
           row["split"] not in {"VALIDATION", "COVERAGE_ONLY"} for row in sources):
        raise ValueError("Universidad Libre family leaked outside validation")
    if any(row["institution_family"] == "externado_preparatorios" and
           row["split"] not in {"DEV", "COVERAGE_ONLY"} for row in sources):
        raise ValueError("Externado family has invalid split")
    if any(row["bytes_verified"] and not row["sha256"] for row in sources):
        raise ValueError("Verified bytes missing SHA-256")
    if any(row.get("question_count", 0) and row["source_type"] not in
           {"INSTITUTIONAL_QUESTION_BANK", "INSTITUTIONAL_ASSESSMENT", "OFFICIAL_EXAM"} for row in sources):
        raise ValueError("Coverage guide counted as assessment questions")
    if sha(BENCH / "source_manifest.jsonl") != manifest["source_manifest_sha256"]:
        raise ValueError("Source manifest hash mismatch")
    if sha(BENCH / "questions/dev.jsonl") != manifest["question_manifest_sha256"]:
        raise ValueError("Question manifest hash mismatch")
    if sha(BENCH / "sampling_manifest.json") != manifest["sampling_manifest_sha256"]:
        raise ValueError("Sampling manifest hash mismatch")
    if len(questions) != sample["selected_count"] or len(gold) != 0:
        raise ValueError("Unexpected DEV queue or gold count")
    if any(row["review_status"] != "NEEDS_HUMAN_REVIEW" or
           row["temporal_review_status"] != "UNCERTAIN" for row in questions):
        raise ValueError("Unreviewed items must remain uncertain and unaccepted")
    artifact = ROOT / "tmp/kc_col_ir_v0.1/pool/externado_procesal_full_pool.jsonl"
    if not artifact.exists() or sha(artifact) != sample["pool_artifact_sha256"]:
        raise ValueError("Local frozen full-pool artifact missing or changed")
    pool = read_jsonl(artifact)
    if len(pool) != sample["pool_size"]:
        raise ValueError("Pool count mismatch")
    ranked = sorted((hashlib.sha256((row["source_family"] + row["source_document"] +
                                   row["source_item_number"]).encode("utf-8")).hexdigest(), row)
                    for row in pool)
    chosen = ranked[:sample["selected_count"]]
    expected_ids = {"EXTERNADO-PRIVADO-I-PROCESAL-CIVIL-2011-Q" +
                    row["source_item_number"].zfill(3) for _, row in chosen}
    if expected_ids != {row["question_id"] for row in questions}:
        raise ValueError("DEV sample is not the prescribed hash-ordered sample")
    if manifest["cuda_ready"] or manifest["baseline_gate"]["unlocked"]:
        raise ValueError("CUDA/baseline gate must remain locked below 10 accepted golds")
    return {"status": "PASS", "sources": len(sources), "externado_pool": len(pool),
            "dev_annotation_batch": len(questions), "validation_items": 0,
            "accepted_retrieval_gold": len(gold), "validation_performance_inspected": False,
            "cuda_ready": False, "sampling_sha256": sample["selection_sha256"]}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
