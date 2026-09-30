"""Create profile-specific coverage/mapping artifacts without retrieval outputs."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks/kc_col_ir_v0.1"
REVIEW = BENCH / "review"
CONTROLLED_PROFILE = "KC-COL-IR-CUJ2026-CONTROLLED-v1"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def create_mappings(gold_rows: list[dict], documents: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    docs_by_member = {int(doc["member_index"]): doc for doc in documents}
    mapping_rows: list[dict] = []
    controlled_coverage: list[dict] = []
    competitive_coverage: list[dict] = []
    all_qids = [row.get("question_id") for row in gold_rows]
    if any(not qid for qid in all_qids) or len(all_qids) != len(set(all_qids)):
        raise ValueError("Gold question IDs must be present and unique")

    for gold in gold_rows:
        qid = gold["question_id"]
        unit_map: dict[str, list[str]] = {}
        unit_docs: dict[str, str] = {}
        unit_status: dict[str, str] = {}
        for unit in gold.get("external_evidence_units", []):
            unit_id = unit.get("external_evidence_unit_id")
            match = re.search(r"MEMBER-(\d+)$", unit.get("source_id", ""))
            if not unit_id or not match:
                raise ValueError(f"External unit has no packet member identity: {qid}")
            member_index = int(match.group(1))
            doc = docs_by_member.get(member_index)
            if not doc or unit.get("sha256") != doc.get("source_member_sha256"):
                raise ValueError(f"External unit/member identity mismatch: {qid}/{unit_id}")
            page_numbers = [int(value) for value in re.findall(r"\d+", unit.get("page", ""))]
            if not page_numbers:
                raise ValueError(f"External unit has no physical page locator: {qid}/{unit_id}")
            if len(page_numbers) == 1:
                pages = page_numbers
            elif len(page_numbers) >= 2:
                pages = list(range(page_numbers[0], page_numbers[-1] + 1))
            else:
                pages = []
            if any(page < 1 or page > doc["page_count"] or page in doc.get("empty_pages", []) for page in pages):
                raise ValueError(f"External unit page is not an extractable controlled passage: {qid}/{unit_id}")
            ids = [f"CUJ2026-P{member_index:02d}-{page:04d}-{doc['source_member_sha256'][:12]}" for page in pages]
            unit_map[unit_id] = ids
            unit_docs[unit_id] = doc["doc_id"]
            unit_status[unit_id] = "COMPLETE"
            mapping_rows.append({
                "question_id": qid,
                "external_evidence_unit_id": unit_id,
                "controlled_document_id": doc["doc_id"],
                "controlled_passage_ids": ids,
                "mapping_status": "COMPLETE",
                "review_notes": f"Exact source member hash and nonempty PDF page locator verified; member {member_index}, physical page(s) {','.join(map(str, pages))}.",
            })

        sets = gold.get("external_minimal_evidence_sets", [])
        if not sets or any(not set(unit_set) <= set(unit_map) for unit_set in sets):
            raise ValueError(f"External minimal evidence sets do not map fully: {qid}")
        controlled_sets = []
        for unit_set in sets:
            passage_set = list(dict.fromkeys(pid for unit_id in unit_set for pid in unit_map[unit_id]))
            if not passage_set:
                raise ValueError(f"Empty controlled minimal evidence set: {qid}")
            controlled_sets.append(passage_set)
        controlled_coverage.append({
            "question_id": qid,
            "profile_id": CONTROLLED_PROFILE,
            "controlled_corpus_coverage": "COMPLETE",
            "controlled_corpus_minimal_evidence_sets": controlled_sets,
            "controlled_gold_document_ids": sorted(set(unit_docs.values())),
            "external_evidence_unit_count": len(unit_map),
            "controlled_mapping_status": "PASSAGE_IDS_VERIFIED_FROM_FROZEN_PROFILE; MATERIALIZATION_STATUS_IN_PROFILE",
        })
        competitive_coverage.append({
            "question_id": qid,
            "profile_id": "corpus-v0.1",
            "competitive_corpus_coverage": "MISSING",
            "matching_document_ids": [],
            "matching_passage_ids": [],
            "review_method": "Frozen source-manifest/document-identity and full-text audit; JEP CUJ 2026 packet is absent from the competitive snapshot.",
        })
    return mapping_rows, controlled_coverage, competitive_coverage


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
                    encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write profile-specific coverage artifacts")
    args = parser.parse_args()
    gold = read_jsonl(BENCH / "gold/dev.jsonl")
    docs = read_jsonl(REVIEW / "controlled_cuj2026_v1_documents.jsonl")
    maps, controlled, competitive = create_mappings(gold, docs)
    result = {"status": "PASS", "accepted_gold": len(gold), "mapping_rows": len(maps),
              "controlled_complete": len(controlled), "competitive_missing": len(competitive),
              "controlled_complete_rate": 1.0 if controlled else None,
              "competitive_missing_rate": 1.0 if competitive else None,
              "retrieval_executed": False}
    if args.write:
        write_jsonl(REVIEW / "controlled_cuj2026_v1_mapping.jsonl", maps)
        write_jsonl(REVIEW / "controlled_cuj2026_v1_coverage.jsonl", controlled)
        write_jsonl(REVIEW / "competitive_corpus_v01_coverage.jsonl", competitive)
    else:
        result["write_status"] = "DRY_RUN_NO_ARTIFACTS_WRITTEN"
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
