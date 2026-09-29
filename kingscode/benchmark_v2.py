"""Small source-extractive pipeline pilot, not a selectable legal benchmark.

Complex legal questions require human authorship/review. No model-generated
paraphrases, official sample, v1 gold or legal answers enter construction.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import random
import re
import time

from jsonschema import Draft202012Validator

from .common import ROOT, digest, file_hash, indexable, read_json, read_jsonl, write_json, write_jsonl
from .metadata import canonical_document_id, canonical_fragment_id

DIRECTORY = ROOT / "benchmarks/kingscode_ir_v2"
CATEGORIES = ["EXACT_REFERENCE", "SEMANTIC_RULE", "CONCEPT", "SCENARIO_APPLICATION", "MULTI_EVIDENCE",
              "TEMPORAL", "JURISPRUDENCE", "NORM_VS_CASELAW", "EXCEPTION", "GRAPH_RELATION"]


def pilot_records(passages):
    """Twelve separate document families, round-robin legal areas, seed zero."""
    groups = defaultdict(list)
    fragment_counts = Counter(canonical_fragment_id(p) for p in passages)
    for p in sorted(passages, key=lambda p: p["passage_id"]):
        if (not indexable(p) or not p.get("article") or p["doc_id"] == "ley_137_de_1994"
                or fragment_counts[canonical_fragment_id(p)] != 1):
            continue
        body = p["text"][len(p.get("text_prefix", "")):]
        # Literal source caption, not a model-written semantic question.
        caption = re.search(r"<([^<>\n]{8,120})>", body[:300])
        if caption is None:
            caption = re.search(r"^ART[IÍ]CULO\s+\d+(?:[.,]\d+)*(?:\s*[A-Za-z]\b)?\s*[.°º]\s*([^.<\n]{8,120})[.\n]", body[:300], re.I)
        if not caption or re.search(r"derogad|modificad|inexequib", caption[1], re.I):
            continue
        area = (p.get("areas") or ["unspecified"])[0]
        groups[area].append((p, caption[1]))
    rng = random.Random(0)
    for values in groups.values(): rng.shuffle(values)
    names = sorted(groups); rng.shuffle(names)
    chosen, documents = [], set()
    while len(chosen) < 12 and any(groups.values()):
        for area in names:
            while groups[area]:
                p, caption = groups[area].pop()
                doc = canonical_document_id(p)
                if doc not in documents:
                    chosen.append((p, caption)); documents.add(doc); break
            if len(chosen) == 12: break
    if len(chosen) < 12:
        raise ValueError(f"Need 12 distinct caption-bearing source documents; found {len(chosen)}")
    bundles = {s: [] for s in ("dev", "validation", "holdout")}
    for i, (p, caption) in enumerate(chosen):
        case_id = f"KC2-PILOT-{i+1:03d}"
        category = "EXACT_REFERENCE" if i % 2 == 0 else "CONCEPT"
        text = f"{p['norm_name']}, artículo {p['article']}" if category == "EXACT_REFERENCE" else caption
        question = {"id": case_id, "question": text, "area": (p.get("areas") or ["unspecified"])[0],
                    "format": "retrieval", "category": category}
        fid = canonical_fragment_id(p)
        gold = {"id": case_id, "record_type": "TECHNICAL_PILOT_ONLY", "gold_document_ids": [canonical_document_id(p)],
                "gold_fragment_ids": [fid], "evidence": [{"canonical_fragment_id": fid, "relevance": "direct"}],
                "minimal_evidence_sets": [[{"canonical_fragment_id": fid, "relevance": "direct"}]],
                "gold_spans": [{"canonical_fragment_id": fid, "passage_id": p["passage_id"],
                                "clean_start": p["clean_start"], "clean_end": p["clean_end"]}],
                "annotation": "Literal source locator/caption pilot; relevance alternatives require human review."}
        provenance = {"id": case_id, "method": "deterministic_source_metadata_or_verbatim_caption_v1",
                      "source_url": p["source_url"], "source_sha256": p["source_sha256"],
                      "passage_id": p["passage_id"], "canonical_document_id": canonical_document_id(p),
                      "caption": caption, "human_review": "pending", "competitive": False}
        split = "dev" if i < 6 else "validation" if i < 9 else "holdout"
        bundles[split].append((question, gold, provenance))
    return bundles


def complete_evidence_set_at_k(passages, gold, k: int) -> int | None:
    """1 when any complete alternative evidence set is present by rank k."""
    alternatives = gold.get("minimal_evidence_sets")
    if not alternatives:
        return None
    from .metadata import canonical_fragment_id
    found = {
        p.get("canonical_fragment_id") or canonical_fragment_id(p)
        for p in passages[:k]
    }
    for evidence_set in alternatives:
        required = {item["canonical_fragment_id"] for item in evidence_set}
        if required and required.issubset(found):
            return 1
    return 0


def build(corpus: Path, directory: Path = DIRECTORY):
    if (directory / "manifest.json").exists():
        raise FileExistsError("Pilot already frozen; do not overwrite after inspection")
    bundles = pilot_records(read_jsonl(corpus / "passages.jsonl"))
    validator = Draft202012Validator(read_json(directory / "question.schema.json"))
    gold_validator = Draft202012Validator(read_json(directory / "gold.schema.json"))
    queue = []
    for split, rows in bundles.items():
        for q, g, _ in rows:
            validator.validate(q)
            gold_validator.validate(g)
        write_jsonl(directory / f"questions/{split}.jsonl", [r[0] for r in rows])
        write_jsonl(directory / f"gold/{split}.jsonl", [r[1] for r in rows])
        write_jsonl(directory / f"authoring/{split}_provenance.jsonl", [r[2] for r in rows])
        # Complex queue uses DEV sources only. No leaked holdout excerpts in a
        # queue that authors will work on during development.
        if split == "dev":
            for category in CATEGORIES:
                if category not in {"EXACT_REFERENCE", "CONCEPT"}:
                    queue.append({"category": category, "status": "needs_human_source_selection_and_question",
                                  "question": None, "gold": None,
                                  "source_candidates": [r[2] for r in rows],
                                  "review_requirements": ["official evidence", "non-leading wording", "complete alternative evidence", "no v1/official gold reuse", "reviewer and rationale", "split-family isolation"]})
    write_jsonl(directory / "authoring/review_queue.jsonl", queue)
    source_manifest = directory / "source_manifest.jsonl"
    manifest = {"version": "benchmark-v2-pilot-0.2",
                "status": "technical_pilot_not_selectable_independent_source_benchmark_unpopulated",
                "independent_source_items": 0, "retrieval_gold_count": 0, "end_to_end_only_count": 0,
                "sealed_eval_count": 0,
                "source_manifest_sha256": file_hash(source_manifest) if source_manifest.exists() else None,
                "seed": 0, "schema_sha256": file_hash(directory / "question.schema.json"),
                "gold_schema_sha256": file_hash(directory / "gold.schema.json"),
                "corpus_sha256": file_hash(corpus / "passages.jsonl"), "corpus_version": read_json(corpus / "manifest.json")["version"],
                "splits": {s: len(rows) for s, rows in bundles.items()}, "document_families_disjoint": True,
                "categories": CATEGORIES, "complex_cases_human_review_pending": len(queue),
                "holdout_policy": "sealed; no evaluation command until separately authorized after reviewed benchmark release",
                "hashes": {p.relative_to(directory).as_posix(): file_hash(p) for p in sorted(directory.rglob("*.jsonl"))
                           if p.name != "source_manifest.jsonl"}}
    write_json(directory / "manifest.json", manifest)
    return manifest


def check(directory: Path = DIRECTORY):
    manifest = read_json(directory / "manifest.json")
    if file_hash(directory / "question.schema.json") != manifest["schema_sha256"]:
        raise ValueError("Schema changed")
    if file_hash(directory / "gold.schema.json") != manifest["gold_schema_sha256"]:
        raise ValueError("Gold schema changed")
    for name, expected in manifest["hashes"].items():
        if file_hash(directory / name) != expected: raise ValueError(f"Pilot changed: {name}")
    source_manifest = directory / "source_manifest.jsonl"
    expected_source_hash = manifest.get("source_manifest_sha256")
    if expected_source_hash is not None and file_hash(source_manifest) != expected_source_hash:
        raise ValueError("Source manifest changed")
    # Hash sealed files but never parse holdout questions/gold for this check.
    validator = Draft202012Validator(read_json(directory / "question.schema.json"))
    for split in ("dev", "validation"):
        for q in read_jsonl(directory / f"questions/{split}.jsonl"): validator.validate(q)
    return {"status": "checked", "hashes": len(manifest["hashes"]), "holdout_parsed": False,
            "selectable": False, "manifest_sha256": file_hash(directory / "manifest.json")}


def evaluate_dev(retrieve, corpus: Path, directory: Path = DIRECTORY, output: Path | None = None):
    check(directory)
    manifest = read_json(directory / "manifest.json")
    if file_hash(corpus / "passages.jsonl") != manifest["corpus_sha256"]:
        raise ValueError("Pilot corpus mismatch")
    questions = read_jsonl(directory / "questions/dev.jsonl")
    ranked = []
    for question in questions:
        start = time.perf_counter()
        result = retrieve(question["question"], 10, "off")
        ranked.append((question, result, (time.perf_counter()-start)*1000))
    # Critical boundary: no gold parsed before all retrieval calls complete.
    gold = {g["id"]: g for g in read_jsonl(directory / "gold/dev.jsonl")}
    from .retrieval_benchmark import per_question_metrics, aggregate, classify_failure
    rows = []
    for q, ps, ms in ranked:
        item_gold = gold[q["id"]]
        metrics = per_question_metrics(ps, item_gold)
        metrics["Complete Evidence Set@8"] = complete_evidence_set_at_k(ps, item_gold, 8)
        metrics["Complete Evidence Set@10"] = complete_evidence_set_at_k(ps, item_gold, 10)
        rows.append({"id": q["id"], "metrics": metrics,
                     "latency_ms": ms, "failure": classify_failure(ps, ps, item_gold, []),
                     "passage_ids": [p["passage_id"] for p in ps]})
    result = {"status": "passed", "scope": "CPU technical pilot only; no architecture selection",
              "benchmark_manifest_sha256": file_hash(directory / "manifest.json"),
              "split": "dev", "metrics": aggregate(rows), "per_question": rows,
              "label_boundary": "all rankings before gold", "holdout_executed": False}
    if output: write_json(output, result)
    return result
