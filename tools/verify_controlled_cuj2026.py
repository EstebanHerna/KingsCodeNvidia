"""Verify the materialized CUJ 2026 controlled corpus and its frozen mappings."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks/kc_col_ir_v0.1"
CORPUS = ROOT / "tmp/kc_col_ir_v0.1/controlled_cuj2026_v1"
PROFILE_ID = "KC-COL-IR-CUJ2026-CONTROLLED-v1"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_numbers(locator: str) -> list[int]:
    values = [int(v) for v in re.findall(r"\d+", locator)]
    if len(values) <= 1:
        return values
    return list(range(values[0], values[-1] + 1))


def ranking_readiness(coverage_rows: list[dict], passage_file_exists: bool) -> dict:
    complete = sum(r.get("controlled_corpus_coverage") == "COMPLETE" for r in coverage_rows)
    # Materialization is a prerequisite to count a gold item as ranking-ready.
    ranking_n = complete if passage_file_exists else 0
    return {"controlled_complete_coverage_n": complete, "ranking_n": ranking_n,
            "unlocked": passage_file_exists and ranking_n >= 10}


def validate_mappings(gold_rows: list[dict], mapping_rows: list[dict], coverage_rows: list[dict],
                      passages: list[dict], documents: list[dict]) -> dict:
    by_q_unit = {(r["question_id"], r["external_evidence_unit_id"]): r for r in mapping_rows}
    if len(by_q_unit) != len(mapping_rows):
        raise ValueError("Duplicate external evidence mapping row")
    passages_by_id = {p["passage_id"]: p for p in passages}
    docs = {d["doc_id"]: d for d in documents}
    if len(passages_by_id) != len(passages):
        raise ValueError("Duplicate controlled passage ID")
    if len(docs) != len(documents):
        raise ValueError("Duplicate controlled document ID")
    expected_keys = set()
    coverage = {r["question_id"]: r for r in coverage_rows}
    if len(coverage) != len(coverage_rows):
        raise ValueError("Duplicate controlled coverage row")
    for gold in gold_rows:
        qid = gold["question_id"]
        if qid not in coverage or coverage[qid].get("controlled_corpus_coverage") != "COMPLETE":
            raise ValueError(f"Controlled coverage is not COMPLETE: {qid}")
        unit_pages = {}
        for unit in gold["external_evidence_units"]:
            key = (qid, unit["external_evidence_unit_id"])
            expected_keys.add(key)
            mapping = by_q_unit.get(key)
            if mapping is None or mapping.get("mapping_status") != "COMPLETE":
                raise ValueError(f"Mapping absent/incomplete: {qid}/{unit['external_evidence_unit_id']}")
            if mapping["controlled_document_id"] not in docs:
                raise ValueError(f"Mapped document absent: {qid}/{unit['external_evidence_unit_id']}")
            doc = docs[mapping["controlled_document_id"]]
            if unit.get("sha256") != doc.get("source_member_sha256"):
                raise ValueError(f"Mapped source member hash differs: {qid}/{unit['external_evidence_unit_id']}")
            expected_pages = page_numbers(unit["page"])
            ids = mapping.get("controlled_passage_ids", [])
            if not ids or len(ids) != len(expected_pages):
                raise ValueError(f"Mapped page set is empty/incomplete: {qid}/{unit['external_evidence_unit_id']}")
            for passage_id, page_no in zip(ids, expected_pages):
                p = passages_by_id.get(passage_id)
                if p is None:
                    raise ValueError(f"Mapped passage absent: {qid}/{unit['external_evidence_unit_id']}/{passage_id}")
                if passage_id == unit["external_evidence_unit_id"]:
                    raise ValueError(f"External evidence ID masquerades as passage ID: {qid}/{passage_id}")
                if p.get("doc_id") != doc["doc_id"] or p.get("source_page") != page_no:
                    raise ValueError(f"Passage document/page mismatch: {qid}/{unit['external_evidence_unit_id']}/{passage_id}")
                unit_pages[unit["external_evidence_unit_id"]] = ids
        mapped_sets = coverage[qid].get("controlled_corpus_minimal_evidence_sets", [])
        external_sets = gold.get("external_minimal_evidence_sets", [])
        expected_sets = [list(dict.fromkeys(pid for uid in group for pid in unit_pages[uid])) for group in external_sets]
        if not mapped_sets or any(not group for group in mapped_sets) or mapped_sets != expected_sets:
            raise ValueError(f"Controlled minimal evidence sets mismatch: {qid}")
        gold_docs = set(coverage[qid].get("controlled_gold_document_ids", []))
        if not gold_docs or not gold_docs <= set(docs):
            raise ValueError(f"Controlled coverage references missing documents: {qid}")
    if set(by_q_unit) != expected_keys:
        raise ValueError("Mapping ledger contains missing or extraneous evidence units")
    if set(coverage) != {g["question_id"] for g in gold_rows}:
        raise ValueError("Controlled coverage question set mismatch")
    return {"gold_questions": len(gold_rows), "mapping_rows": len(mapping_rows),
            "controlled_complete": len(coverage), "mapped_passages": len({p for r in mapping_rows for p in r["controlled_passage_ids"]})}


def verify() -> dict:
    sys.path.insert(0, str(ROOT))
    from kingscode.common import indexable
    from kingscode.retrieval import BM25Index, TOKENIZER_VERSION, Retriever
    from tools.build_controlled_cuj2026 import build

    profile = read_json(BENCH / "review/controlled_cuj2026_v1_profile.json")
    runtime = read_json(CORPUS / "manifest.json")
    documents = read_jsonl(BENCH / "review/controlled_cuj2026_v1_documents.jsonl")
    inventory = read_jsonl(BENCH / "review/controlled_cuj2026_v1_source_inventory.jsonl")
    passages = read_jsonl(CORPUS / "passages.jsonl")
    mappings = read_jsonl(BENCH / "review/controlled_cuj2026_v1_mapping.jsonl")
    coverage = read_jsonl(BENCH / "review/controlled_cuj2026_v1_coverage.jsonl")
    competitive = read_jsonl(BENCH / "review/competitive_corpus_v01_coverage.jsonl")
    gold = read_jsonl(BENCH / "gold/dev.jsonl")

    if profile.get("profile_id") != PROFILE_ID or runtime.get("profile_id") != PROFILE_ID:
        raise ValueError("Controlled profile identity mismatch")
    if profile.get("materialized") is not True or profile.get("build_status") != "MATERIALIZED_VERIFIED":
        raise ValueError("Controlled profile is not marked materialized")
    if len(documents) != 6 or profile.get("document_count") != 6 or len(runtime.get("documents", [])) != 6:
        raise ValueError("Controlled profile must contain exactly six eligible PDFs")
    if len(inventory) != 18 or sum(d["page_count"] for d in documents) != 191:
        raise ValueError("Controlled ZIP inventory/page count mismatch")
    kinds = {kind: sum(row["classification"] == kind for row in inventory)
             for kind in ("TEXTUAL_PDF_CANDIDATE", "AUDIO", "DIRECTORY_METADATA", "ARCHIVE_METADATA", "UNSUPPORTED_BINARY")}
    if kinds != {"TEXTUAL_PDF_CANDIDATE": 6, "AUDIO": 2, "DIRECTORY_METADATA": 1,
                 "ARCHIVE_METADATA": 9, "UNSUPPORTED_BINARY": 0}:
        raise ValueError(f"Unexpected archive member classification: {kinds}")
    if len(passages) != 190 or runtime.get("passage_count") != 190:
        raise ValueError("Controlled nonempty passage count mismatch")
    archive_sha = "3f9dc1765e8ea18588c13a48e1785b506f6a0c06eef3743057e2d34097d9b101"
    if sha(ROOT / "tmp/kc_col_ir_v0.1/raw/jep-primary/expediente_concurso_jep_2026.zip") != archive_sha:
        raise ValueError("Official CUJ ZIP SHA mismatch")
    if runtime.get("source_archive_sha256") != archive_sha or profile.get("source_archive_sha256") != archive_sha:
        raise ValueError("Controlled archive provenance mismatch")
    if sha(CORPUS / "passages.jsonl") != runtime.get("passages_sha256") or profile.get("passages_sha256") != runtime.get("passages_sha256"):
        raise ValueError("Controlled passages SHA mismatch")
    if sha(CORPUS / "manifest.json") != profile.get("controlled_manifest_sha256"):
        raise ValueError("Controlled runtime manifest SHA mismatch")
    if sha(CORPUS / "index/bm25.json") != runtime["index_files"].get("index/bm25.json") or profile.get("bm25_index_sha256") != runtime["index_files"].get("index/bm25.json"):
        raise ValueError("BM25 index SHA mismatch")
    if runtime.get("controlled_corpus_fingerprint") != profile.get("controlled_corpus_fingerprint"):
        raise ValueError("Controlled profile fingerprint mismatch")
    if runtime.get("pypdf_version") != "6.10.0" or profile.get("parser") != "pypdf-6.10.0-page-extract-text":
        raise ValueError("Parser version mismatch")
    if profile.get("passages_hash_semantics") != runtime.get("passages_hash_semantics"):
        raise ValueError("Passage hash semantics differ between profile and build manifest")
    old_schema_rows = [{k: v for k, v in row.items() if k != "member_index"} for row in passages]
    old_schema_bytes = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in old_schema_rows).encode("utf-8")
    old_schema_sha = hashlib.sha256(old_schema_bytes).hexdigest()
    if old_schema_sha != "019dee8a805e87fbacfce45cd448f4b538b921d6d7c5aa7ff3a82a5472a894ef":
        raise ValueError("Previously reported in-memory extraction hash semantics could not be reproduced")
    if profile.get("previous_in_memory_extraction_sha256") != old_schema_sha:
        raise ValueError("Prior extraction hash explanation does not match the verified prior schema")
    by_doc = {d["doc_id"]: d for d in documents}
    members = {m["member_index"]: m for m in inventory}
    for p in passages:
        doc = by_doc.get(p["doc_id"])
        if doc is None or p.get("canonical_document_id") != doc["doc_id"]:
            raise ValueError(f"Passage references unknown/noncanonical document: {p.get('passage_id')}")
        if p.get("source_member_sha256") != doc["source_member_sha256"] or p.get("source_archive_sha256") != archive_sha:
            raise ValueError(f"Passage source hash provenance mismatch: {p['passage_id']}")
        if p.get("member_index") != doc["member_index"] or p.get("source_member_path") != doc["member_path"]:
            raise ValueError(f"Passage member provenance mismatch: {p['passage_id']}")
        member = members.get(p["member_index"])
        expected_id = f"CUJ2026-P{p['member_index']:02d}-{p['source_page']:04d}-{doc['source_member_sha256'][:12]}"
        if not member or member.get("member_sha256") != doc["source_member_sha256"] or p["passage_id"] != expected_id:
            raise ValueError(f"Passage ID/member hash identity mismatch: {p['passage_id']}")
        if not p.get("text", "").strip():
            raise ValueError(f"Empty page was emitted as a passage: {p['passage_id']}")
        if p.get("retrieval_eligible") is not True or p.get("parser_version") != "pypdf-6.10.0-page-extract-text":
            raise ValueError(f"Passage eligibility/parser metadata invalid: {p['passage_id']}")
        if any(word in p for word in ("expected_answer", "gold_label", "evidence_unit_id")):
            raise ValueError(f"Gold metadata leaked into passage: {p['passage_id']}")

    mapping_result = validate_mappings(gold, mappings, coverage, passages, documents)
    if not ranking_readiness(coverage, (CORPUS / "passages.jsonl").is_file())["unlocked"]:
        raise ValueError("Materialized controlled corpus has fewer than ten complete gold mappings")
    if len(competitive) != 10 or any(r.get("competitive_corpus_coverage") != "MISSING" for r in competitive):
        raise ValueError("Competitive corpus missing profile must remain 10/10 MISSING")
    indexed_passages = [p for p in passages if indexable(p)]
    index = BM25Index.load(CORPUS / "index/bm25.json", indexed_passages, runtime["passages_sha256"])
    if runtime.get("tokenizer_version") != TOKENIZER_VERSION:
        raise ValueError("Tokenizer version differs from Retriever")
    if [p["passage_id"] for p in index.passages] != [p["passage_id"] for p in indexed_passages]:
        raise ValueError("BM25 passage ordering differs from corpus")
    opened = Retriever(CORPUS, mode="bm25", rerank=False, candidate_k=30, graph_budget=0, graph_router=lambda _: False)
    if len(opened.passages) != 190 or opened.corpus_hash != runtime["passages_sha256"]:
        raise ValueError("Retriever CPU index reopen mismatch")
    repeat = build(materialize=False)
    if repeat["passages_sha256"] != runtime["passages_sha256"] or repeat["build_sha256"] != runtime["controlled_corpus_fingerprint"]:
        raise ValueError("Repeated deterministic build differs from materialized corpus")
    tracked_tmp = subprocess.check_output(["git", "ls-files", "tmp"], cwd=ROOT, text=True).splitlines()
    if tracked_tmp:
        raise ValueError("Raw or derived tmp artifacts are tracked in Git")
    return {"status": "PASS", "profile_id": PROFILE_ID, "documents": len(documents),
            "physical_pages": sum(d["page_count"] for d in documents), "passages": len(passages),
            "archive_members": len(inventory), "member_classifications": kinds,
            "passages_sha256": runtime["passages_sha256"],
            "controlled_manifest_sha256": profile["controlled_manifest_sha256"],
            "bm25_sha256": runtime["index_files"]["index/bm25.json"],
            "controlled_corpus_fingerprint": runtime["controlled_corpus_fingerprint"],
            "mapping": mapping_result, "competitive_missing": len(competitive),
            "previous_in_memory_hash_semantics": "Reproduced exactly by serializing the same passages without the explicit member_index provenance field; current serialized SHA adds that required field.",
            "tokenizer_version": TOKENIZER_VERSION, "retriever_open_smoke": "PASS_NO_QUERY_EXECUTED",
            "deterministic_rebuild": "PASS", "cuda_executed": False, "retrieval_executed": False}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
