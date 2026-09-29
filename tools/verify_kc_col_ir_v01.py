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
    dispositions = read_jsonl(BENCH / "review/jep_2025_dispositions.jsonl")
    acquisitions = read_jsonl(BENCH / "review/primary_source_acquisitions.jsonl")
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
    if len(questions) != sample["selected_count"] or len(legacy) != old_sample["selected_count"]:
        raise ValueError("Unexpected candidate queue or gold count")
    question_ids = {row["question_id"] for row in questions}
    if len(dispositions) != 30 or {row["question_id"] for row in dispositions} != question_ids:
        raise ValueError("JEP dispositions must preserve exactly the frozen 30 IDs")
    allowed_dispositions = {"RETRIEVAL_GOLD_CANDIDATE", "FACTUAL_CLARIFICATION_ONLY",
                            "LEGAL_STRATEGY_NOT_ANSWERED", "EXPLICIT_REFERENCE_LOW_DIFFICULTY",
                            "ANSWER_NOT_SUFFICIENT_FOR_GOLD", "AMBIGUOUS", "REJECTED"}
    if any(row.get("disposition") not in allowed_dispositions for row in dispositions):
        raise ValueError("Unknown JEP review disposition")
    if any(row.get("retrieval_performance_used") is not False or row.get("minimal_evidence_sets") != []
           or row.get("temporal_review_status") != "UNCERTAIN"
           or row.get("corpus_coverage_status") != "NOT_ASSESSED_NO_ACCEPTED_GOLD"
           for row in dispositions):
        raise ValueError("Candidate review may not use retrieval, invent evidence sets, or couple gold to corpus coverage")
    if any(k in row for row in dispositions for k in ("retrieval_results", "rankings", "retrieval_score", "recall")):
        raise ValueError("Retrieval-derived annotation field found")
    if manifest["counts"].get("accepted_retrieval_gold") != len(gold):
        raise ValueError("Manifest accepted-gold count mismatch")
    gold_by_id = {row["question_id"]: row for row in gold}
    if len(gold_by_id) != len(gold) or not set(gold_by_id) <= question_ids:
        raise ValueError("Accepted gold must map one-to-one to frozen DEV question IDs")
    for qid, row in gold_by_id.items():
        if row.get("review_status") != "ACCEPTED_RETRIEVAL_GOLD" or not row.get("minimal_evidence_sets") or \
           any(not evidence_set for evidence_set in row.get("minimal_evidence_sets", [])):
            raise ValueError(f"Accepted gold lacks review status/evidence sets: {qid}")
        if not row.get("evidence_sources") or row.get("temporal_review_status") not in {
                "CURRENTLY_SUPPORTABLE", "HISTORICAL_ONLY", "NOT_APPLICABLE"}:
            raise ValueError(f"Accepted gold lacks independent source provenance/temporal review: {qid}")
        if any(not source.get("source_id") or not source.get("sha256") or not source.get("source_url")
               for source in row["evidence_sources"]):
            raise ValueError(f"Accepted gold source provenance is incomplete: {qid}")
        if row.get("corpus_coverage") not in {"COMPLETE", "PARTIAL", "MISSING", "AMBIGUOUS"}:
            raise ValueError(f"Accepted gold has invalid corpus coverage: {qid}")
    counts = {name: sum(row["disposition"] == name for row in dispositions) for name in allowed_dispositions}
    if counts["RETRIEVAL_GOLD_CANDIDATE"] != 13 or counts["EXPLICIT_REFERENCE_LOW_DIFFICULTY"] != 5 or \
       counts["FACTUAL_CLARIFICATION_ONLY"] != 3 or counts["LEGAL_STRATEGY_NOT_ANSWERED"] != 6 or \
       counts["ANSWER_NOT_SUFFICIENT_FOR_GOLD"] != 3 or counts["REJECTED"] != 0 or counts["AMBIGUOUS"] != 0:
        raise ValueError(f"Unexpected human/source review disposition counts: {counts}")
    if any(not row.get("sha256") or not row.get("final_url") or not row.get("retrieved_at_utc")
           or not row.get("document_identity") for row in acquisitions):
        raise ValueError("Acquired-source provenance incomplete")
    if len({row["source_id"] for row in acquisitions}) != len(acquisitions) or \
       any(len(row["sha256"]) != 64 or not row.get("source_url") or not row.get("bytes")
           or not row.get("signature") for row in acquisitions):
        raise ValueError("Acquired-source identity, hash, byte count, URL or signature invalid")
    members = [row for row in acquisitions if row.get("parent_archive_source_id")]
    archive = next(row for row in acquisitions if row["source_id"] == "JEP-CUJ-2025-EXPEDIENTE-ZIP")
    if len(members) != 22 or any(row["parent_archive_sha256"] != archive["sha256"] for row in members):
        raise ValueError("Official expediente member provenance does not resolve to its archive")
    externado = next(row for row in sources if row["source_id"] == "EXTERNADO-PRIVADO-I-PROCESAL-CIVIL-2011")
    if externado["split"] != "REPRODUCIBILITY_ONLY" or externado["exposure_status"] != \
       "ACQUIRED_HASHED_MECHANICAL_POOL_REPRODUCIBILITY_ONLY":
        raise ValueError("Externado must stay reproducibility-only")
    if any(row["review_status"] != "NEEDS_HUMAN_REVIEW" or row["temporal_review_status"] != "UNCERTAIN"
           for row in questions if row["question_id"] not in gold_by_id) or \
       any(row["review_status"] != "NEEDS_HUMAN_REVIEW" or row["temporal_review_status"] != "UNCERTAIN" for row in legacy):
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
            "review_dispositions": counts, "acquired_source_artifacts": len(acquisitions),
            "expediente_pdf_members": len(members),
            "accepted_retrieval_gold": len(gold), "validation_performance_inspected": False,
            "cuda_ready": False, "sampling_sha256": sample["selection_sha256"]}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
