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
    legacy = read_jsonl(BENCH / "questions/reproducibility_externado_2011.jsonl")
    gold = read_jsonl(BENCH / "gold/dev.jsonl")
    sample = json.loads((BENCH / "sampling_manifest.json").read_text(encoding="utf-8"))
    old_sample = json.loads((BENCH / "sampling_manifest_externado_2011.json").read_text(encoding="utf-8"))
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
                     "TOPIC_GUIDE", "METHODOLOGY_GUIDE", "OFFICIAL_ACADEMIC_LEGAL_COMPETITION",
                     "UNIVERSITY_MOOT_CLARIFICATION_RESPONSES"}
    if any(row["source_type"] not in allowed_types for row in sources):
        raise ValueError("Unknown source type")
    allowed = {
        "universidad_libre_preparatorios": {"VALIDATION", "VALIDATION_CANDIDATE", "COVERAGE_ONLY"},
        "externado_preparatorios": {"REPRODUCIBILITY_ONLY", "COVERAGE_ONLY"},
        "jep_concurso_universitario_2025": {"DEV_CANDIDATE"},
        "jep_concurso_universitario_2026": {"DISCOVERY_ONLY"},
        "javeriana_moot_seguros_2026": {"VALIDATION_CANDIDATE"},
        "externado_asobancaria_moot_financiero_2025": {"SEALED_FUTURE"},
    }
    for row in sources:
        if row["institution_family"] in allowed and row["split"] not in allowed[row["institution_family"]]:
            raise ValueError(f"Invalid split for {row['institution_family']}")
    if any(row["bytes_verified"] and not row["sha256"] for row in sources):
        raise ValueError("Verified bytes missing SHA-256")
    if any(row.get("question_count", 0) and row["source_type"] not in
           {"INSTITUTIONAL_QUESTION_BANK", "INSTITUTIONAL_ASSESSMENT", "OFFICIAL_EXAM",
            "OFFICIAL_ACADEMIC_LEGAL_COMPETITION"} for row in sources):
        raise ValueError("Coverage guide counted as assessment questions")
    if sha(BENCH / "source_manifest.jsonl") != manifest["source_manifest_sha256"]:
        raise ValueError("Source manifest hash mismatch")
    if sha(BENCH / "questions/dev.jsonl") != manifest["question_manifest_sha256"]:
        raise ValueError("Question manifest hash mismatch")
    if sha(BENCH / "sampling_manifest.json") != manifest["sampling_manifest_sha256"]:
        raise ValueError("Sampling manifest hash mismatch")
    if sha(BENCH / "questions/reproducibility_externado_2011.jsonl") != manifest["legacy_reproducibility_questions_sha256"]:
        raise ValueError("Legacy reproducibility question hash mismatch")
    if sha(BENCH / "sampling_manifest_externado_2011.json") != manifest["legacy_reproducibility_sampling_sha256"]:
        raise ValueError("Legacy sampling manifest hash mismatch")
    if len(questions) != sample["selected_count"] or len(legacy) != old_sample["selected_count"] or len(gold) != 0:
        raise ValueError("Unexpected candidate queue or gold count")
    if any(row["review_status"] != "NEEDS_HUMAN_REVIEW" or row["temporal_review_status"] != "UNCERTAIN" for row in questions + legacy):
        raise ValueError("Unreviewed items must remain uncertain and unaccepted")
    if {row["source_family"] for row in questions} != {"jep_concurso_universitario_2025"}:
        raise ValueError("Primary DEV candidate queue must contain only the JEP 2025 family")
    if {row["source_id"] for row in legacy} != {"EXTERNADO-PRIVADO-I-PROCESAL-CIVIL-2011"}:
        raise ValueError("Legacy reproducibility queue must contain only Externado")
    jep_pool_path = ROOT / "tmp/kc_col_ir_v0.1/pool/jep_cuj_2025_full_pool.jsonl"
    if not jep_pool_path.exists() or sha(jep_pool_path) != sample["pool_artifact_sha256"]:
        raise ValueError("Local frozen JEP pool missing or changed")
    jep_pool = read_jsonl(jep_pool_path)
    if len(jep_pool) != sample["pool_size"] or sample["pool_size"] != 62:
        raise ValueError("JEP pool count mismatch")
    ranked = sorted((hashlib.sha256((r["source_family"] + r["source_document"] + r["source_item_number"]).encode()).hexdigest(), r) for r in jep_pool)
    expected = {"JEP-CUJ-2025-Q" + str(int(r["source_item_number"])).zfill(3) for _, r in ranked[:sample["selected_count"]]}
    if expected != {r["question_id"] for r in questions}:
        raise ValueError("JEP DEV sample is not prescribed hash-ordered sample")
    externado_path = ROOT / "tmp/kc_col_ir_v0.1/pool/externado_procesal_full_pool.jsonl"
    if not externado_path.exists() or sha(externado_path) != old_sample["pool_artifact_sha256"]:
        raise ValueError("Local Externado reproducibility pool missing or changed")
    externado_pool = read_jsonl(externado_path)
    old_ranked = sorted((hashlib.sha256((r["source_family"] + r["source_document"] + r["source_item_number"]).encode()).hexdigest(), r) for r in externado_pool)
    old_expected = {"EXTERNADO-PRIVADO-I-PROCESAL-CIVIL-2011-Q" + r["source_item_number"].zfill(3) for _, r in old_ranked[:old_sample["selected_count"]]}
    if old_expected != {r["question_id"] for r in legacy}:
        raise ValueError("Externado reproducibility sample changed")
    if manifest["cuda_ready"] or manifest["baseline_gate"]["unlocked"]:
        raise ValueError("CUDA/baseline gate must remain locked below 10 accepted golds")
    if manifest["validation_exposure"]["parsed"] or manifest["validation_exposure"]["retrieval_performance_inspected"]:
        raise ValueError("Validation family must remain unparsed and uninspected")
    return {"status": "PASS", "sources": len(sources), "jep_pool": len(jep_pool),
            "primary_dev_annotation_batch": len(questions), "externado_reproducibility_batch": len(legacy),
            "accepted_retrieval_gold": len(gold), "validation_performance_inspected": False,
            "cuda_ready": False, "sampling_sha256": sample["selection_sha256"]}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
