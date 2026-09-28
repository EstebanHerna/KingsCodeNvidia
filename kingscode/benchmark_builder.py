"""Build and validate the deterministic KingsCode internal IR benchmark.

The builder uses only the frozen official-corpus snapshot: legal metadata,
article/section locators, graph evidence already grounded in source text, and
exact source passage offsets. It never reads the official development sample,
answers, or legal_basis. It never calls a language model.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

from .common import ROOT, file_hash, indexable, read_json, read_jsonl, write_json, write_jsonl
from .metadata import canonical_document_id, canonical_fragment_id

BENCHMARK_ROOT = ROOT / "benchmarks" / "kingscode_ir"
BENCHMARK_VERSION = "kingscode-ir-v1"
AREAS = [
    "Derecho administrativo", "Derecho civil", "Derecho comercial y sociedades",
    "Derecho constitucional", "Derecho de familia",
    "Derecho de los mercados [competencia, consumidor, datos personales y propiedad intelectual]",
    "Derecho laboral", "Derecho penal", "Derecho procesal", "Derecho tributario",
]
AREA_CODES = {
    "Derecho administrativo": "ADM", "Derecho civil": "CIV", "Derecho comercial y sociedades": "COM",
    "Derecho constitucional": "CON", "Derecho de familia": "FAM",
    "Derecho de los mercados [competencia, consumidor, datos personales y propiedad intelectual]": "MER",
    "Derecho laboral": "LAB", "Derecho penal": "PEN", "Derecho procesal": "PRO",
    "Derecho tributario": "TRI",
}
FORBIDDEN_QUESTION_KEYS = {"gold_document_ids", "gold_fragment_ids", "evidence", "gold_spans",
                           "legal_basis", "expected_answer", "respuesta_correcta", "texto_respuesta_correcta"}


def _schema_validator() -> Draft202012Validator:
    return Draft202012Validator(read_json(BENCHMARK_ROOT / "benchmark.schema.json"))


def _natural_locator(passage: dict) -> tuple:
    article = passage.get("article")
    if article is None:
        return (1, str(passage.get("section") or ""), passage["passage_id"])
    components = []
    for value in str(article).replace(",", ".").replace("-", ".").split("."):
        components.append((0, int(value)) if value.isdigit() else (1, value))
    return (0, tuple(components), passage["passage_id"])


def _locator_label(passage: dict) -> str:
    if passage.get("article"):
        return f"artículo {passage['article']}"
    if passage.get("section"):
        return f"sección «{passage['section']}»"
    return "fragmento estructural"


def _question_single(passage: dict, relation: str | None = None) -> str:
    norm = passage.get("norm_name") or passage.get("title") or canonical_document_id(passage)
    locator = _locator_label(passage)
    if relation:
        return (f"En {norm}, ubique el texto oficial del {locator} que evidencia explícitamente "
                f"la relación jurídica {relation}.")
    if passage.get("source_type") == "decision":
        return f"Ubique el texto oficial de la {locator} de {norm}."
    return f"Ubique el texto oficial del {locator} de {norm}."


def _question_multi(first: dict, second: dict) -> str:
    norm = first.get("norm_name") or first.get("title") or canonical_document_id(first)
    return (f"Ubique los textos oficiales del {_locator_label(first)} y del {_locator_label(second)} "
            f"de {norm}.")


def _source_tags(passage: dict, *, relation: str | None, duplicate_articles: set[str], unseen_docs: set[str]) -> list[str]:
    tags = ["EXPLICIT"]
    if passage.get("source_type") == "decision":
        tags.append("CASELAW")
    if relation:
        tags.append("GRAPH")
    if passage.get("article") and str(passage["article"]) in duplicate_articles:
        tags.append("DISTRACTOR")
    if passage.get("doc_id") in unseen_docs:
        tags.append("UNSEEN_SEED")
    return tags


def _record_gold(case_id: str, evidence: list[dict]) -> dict:
    docs = list(dict.fromkeys(canonical_document_id(p) for p in evidence))
    fragments = list(dict.fromkeys(canonical_fragment_id(p) for p in evidence))
    return {
        "record_type": "gold", "id": case_id, "gold_document_ids": docs,
        "gold_fragment_ids": fragments,
        "evidence": [{"canonical_fragment_id": canonical_fragment_id(p), "relevance": "direct"} for p in evidence],
        "gold_spans": [{"canonical_fragment_id": canonical_fragment_id(p), "passage_id": p["passage_id"],
                        "clean_start": p["clean_start"], "clean_end": p["clean_end"]} for p in evidence],
        "annotation": "Deterministic source-derived locator; exact official corpus passage and offsets verified."
    }


def _corpus_context(corpus: Path) -> tuple[list[dict], dict, list[dict]]:
    manifest = read_json(corpus / "manifest.json")
    all_passages = read_jsonl(corpus / "passages.jsonl")
    eligible = [p for p in all_passages if indexable(p)]
    edges = read_jsonl(corpus / "graph" / "edges.jsonl")
    return eligible, manifest, edges


def _unseen_docs(manifest: dict) -> set[str]:
    # Priority 0 additions were created outside the starter seed inventory. This
    # is corpus provenance metadata only; it is not passed to retrieval.
    return {d["doc_id"] for d in manifest["documentos"] if d.get("priority") == 0}


def _relation_by_passage(edges: list[dict]) -> dict[str, str]:
    result: dict[str, str] = {}
    for edge in edges:
        if edge.get("relation") in {"REMITE_A", "MODIFICA", "DEROGA", "REGLAMENTA", "DESARROLLA", "EXCEPCIONA"}:
            result.setdefault(edge["evidence_passage_id"], edge["relation"])
    return result


def _unique_fragment_candidates(passages: list[dict]) -> list[dict]:
    count = Counter(canonical_fragment_id(p) for p in passages)
    return [p for p in passages if count[canonical_fragment_id(p)] == 1 and p.get("clean_end", 0) > p.get("clean_start", 0)]


def _build_cases(corpus: Path, cases_per_area: int) -> tuple[list[dict], list[dict], list[dict], dict]:
    passages, manifest, edges = _corpus_context(corpus)
    candidates = _unique_fragment_candidates(passages)
    by_area: dict[str, list[dict]] = defaultdict(list)
    for p in candidates:
        for area in p.get("areas") or []:
            if area in AREA_CODES:
                by_area[area].append(p)
    relation_for = _relation_by_passage(edges)
    unseen = _unseen_docs(manifest)
    article_doc_count = defaultdict(set)
    for p in candidates:
        if p.get("article"):
            article_doc_count[str(p["article"])].add(canonical_document_id(p))
    duplicate_articles = {article for article, docs in article_doc_count.items() if len(docs) > 1}

    questions, golds, review_queue = [], [], []
    used_fragments: set[str] = set()
    for area in AREAS:
        local = sorted(by_area[area], key=lambda p: (canonical_document_id(p), _natural_locator(p)))
        # Create source-derived authoring packets for semantic/temporal prompts
        # rather than fabricating those question texts.
        for p in local[:2]:
            review_queue.append({
                "status": "needs_human_review", "needs_human_question_text": True,
                "required_question_type": "SEMANTIC" if len(review_queue) % 2 == 0 else "TEMPORAL",
                "source_document": p.get("norm_name"), "source_url": p.get("source_url"),
                "area": area, "canonical_document_id": canonical_document_id(p),
                "canonical_fragment_id": canonical_fragment_id(p), "passage_id": p["passage_id"],
                "suggested_target_concept": _locator_label(p),
                "why_this_is_useful": "Official source evidence is exact, but a faithful semantic/temporal question requires human legal wording.",
                "source_excerpt": p["text"][:600]
            })

        selected: list[dict] = []
        for p in local:
            if canonical_fragment_id(p) not in used_fragments:
                selected.append(p)
            if len(selected) >= cases_per_area + 10:
                break
        if len(selected) < cases_per_area:
            raise ValueError(f"Insufficient unique eligible source passages for {area}: {len(selected)}")

        # Up to 20% multi-evidence cases are paired within a document when source
        # structure allows it; otherwise cases remain single-evidence rather than
        # introducing uncertain gold.
        multi_target = cases_per_area // 5
        pairs: list[tuple[dict, dict]] = []
        grouped = defaultdict(list)
        for p in selected:
            grouped[canonical_document_id(p)].append(p)
        pair_used: set[str] = set()
        for doc in sorted(grouped):
            values = grouped[doc]
            for first, second in zip(values[::2], values[1::2]):
                if len(pairs) >= multi_target:
                    break
                if canonical_fragment_id(first) not in pair_used and canonical_fragment_id(second) not in pair_used:
                    pairs.append((first, second))
                    pair_used.update({canonical_fragment_id(first), canonical_fragment_id(second)})
            if len(pairs) >= multi_target:
                break
        singles_needed = cases_per_area - len(pairs)
        singles = [p for p in selected if canonical_fragment_id(p) not in pair_used][:singles_needed]
        if len(singles) != singles_needed:
            raise ValueError(f"Cannot construct {cases_per_area} high-confidence cases for {area}")

        case_number = 1
        for first, second in pairs:
            case_id = f"KC-{AREA_CODES[area]}-{case_number:03d}"
            case_number += 1
            tags = _source_tags(first, relation=None, duplicate_articles=duplicate_articles, unseen_docs=unseen)
            tags = list(dict.fromkeys(tags + ["MULTI_EVIDENCE"]))
            questions.append({"record_type": "question", "id": case_id, "question": _question_multi(first, second),
                              "area": area, "format": "retrieval", "tags": tags,
                              "source_derivation": "deterministic_template"})
            golds.append(_record_gold(case_id, [first, second]))
            used_fragments.update({canonical_fragment_id(first), canonical_fragment_id(second)})
        for p in singles:
            case_id = f"KC-{AREA_CODES[area]}-{case_number:03d}"
            case_number += 1
            relation = relation_for.get(p["passage_id"])
            tags = _source_tags(p, relation=relation, duplicate_articles=duplicate_articles, unseen_docs=unseen)
            questions.append({"record_type": "question", "id": case_id, "question": _question_single(p, relation),
                              "area": area, "format": "retrieval", "tags": tags,
                              "source_derivation": "deterministic_template"})
            golds.append(_record_gold(case_id, [p]))
            used_fragments.add(canonical_fragment_id(p))

    stats = {"cases_by_area": dict(Counter(q["area"] for q in questions)),
             "cases_by_tag": dict(Counter(tag for q in questions for tag in q["tags"])),
             "review_queue": len(review_queue), "corpus_hashes": manifest["hashes"],
             "bm25_sha256": manifest["bm25_sha256"]}
    return questions, golds, review_queue, stats


def _split_cases(questions: list[dict], golds: list[dict]) -> dict[str, tuple[list[dict], list[dict]]]:
    gold_by_id = {g["id"]: g for g in golds}
    grouped = defaultdict(list)
    for q in questions:
        grouped[q["area"]].append(q)
    splits = {"dev": [], "validation": [], "holdout": []}
    for area in AREAS:
        values = sorted(grouped[area], key=lambda q: q["id"])
        n = len(values)
        # 60/20/20 applies to 10-case checkpoint and 20-case final benchmark.
        dev_n, validation_n = n * 3 // 5, n // 5
        splits["dev"].extend(values[:dev_n])
        splits["validation"].extend(values[dev_n:dev_n + validation_n])
        splits["holdout"].extend(values[dev_n + validation_n:])
    return {split: (sorted(qs, key=lambda q: q["id"]), sorted([gold_by_id[q["id"]] for q in qs], key=lambda g: g["id"]))
            for split, qs in splits.items()}


def _write_split(split: str, questions: list[dict], golds: list[dict]) -> None:
    write_jsonl(BENCHMARK_ROOT / "questions" / f"{split}.jsonl", questions)
    write_jsonl(BENCHMARK_ROOT / "gold" / f"{split}.jsonl", golds)


def build(corpus: Path | None = None, *, cases_per_area: int = 20) -> dict:
    """Build deterministic v1 artifacts; 10/area is checkpoint, 20/area final."""
    if cases_per_area not in {10, 20}:
        raise ValueError("cases_per_area must be 10 (checkpoint) or 20 (final v1)")
    corpus = corpus or (ROOT / "corpus")
    questions, golds, review_queue, stats = _build_cases(corpus, cases_per_area)
    splits = _split_cases(questions, golds)
    for split, (q, g) in splits.items():
        _write_split(split, q, g)
    write_jsonl(BENCHMARK_ROOT / "authoring" / "review_queue.jsonl", review_queue)
    manifest = {
        "version": BENCHMARK_VERSION, "generated_at": datetime.now(timezone.utc).isoformat(),
        "generation": {"kind": "deterministic_template_over_verified_corpus_metadata", "closed_model_used": False,
                       "cases_per_area": cases_per_area, "target_total": len(questions)},
        "corpus": {"version": read_json(corpus / "manifest.json")["version"], **stats["corpus_hashes"], "bm25_sha256": stats["bm25_sha256"]},
        "schema_sha256": file_hash(BENCHMARK_ROOT / "benchmark.schema.json"),
        "splits": {split: {"questions": len(q), "question_sha256": file_hash(BENCHMARK_ROOT / "questions" / f"{split}.jsonl"),
                            "gold_sha256": file_hash(BENCHMARK_ROOT / "gold" / f"{split}.jsonl")} for split, (q, g) in splits.items()},
        "coverage": {"cases_by_area": stats["cases_by_area"], "cases_by_tag": stats["cases_by_tag"],
                     "human_review_queue": len(review_queue)},
        "holdout_policy": {"protected": True, "allowed_purposes": ["predeclared_baseline", "post_selection_confirmation"],
                           "official_50": "separate external milestone; never benchmark development data"},
        "gold_input_separation": "questions contain no gold/evaluation fields; gold is scored only after rankings are captured"
    }
    write_json(BENCHMARK_ROOT / "manifests" / "benchmark_manifest.json", manifest)
    # This immutable-in-source declaration allows exactly the predeclared R0
    # baseline holdout. Post-selection access is additionally bound to a
    # validation-only selection record by the evaluator.
    write_json(BENCHMARK_ROOT / "manifests" / "holdout_access.json", {
        "version": "holdout-access-v1", "benchmark_manifest_sha256": file_hash(BENCHMARK_ROOT / "manifests" / "benchmark_manifest.json"),
        "predeclared": [{"variant": "R0", "split": "holdout", "purpose": "predeclared_baseline"}],
        "policy": "No other holdout use is allowed absent a validation-only selected_config.json record."
    })
    report = verify(corpus)
    return {"manifest": manifest, "verification": report}


def _read_split(split: str) -> tuple[list[dict], list[dict]]:
    return (read_jsonl(BENCHMARK_ROOT / "questions" / f"{split}.jsonl"),
            read_jsonl(BENCHMARK_ROOT / "gold" / f"{split}.jsonl"))


def verify(corpus: Path | None = None) -> dict:
    """Validate schemas, IDs, splits, spans and strict input/gold separation."""
    corpus = corpus or (ROOT / "corpus")
    validator = _schema_validator()
    corpus_passages = read_jsonl(corpus / "passages.jsonl")
    by_pid = {p["passage_id"]: p for p in corpus_passages}
    fragment_ids = {canonical_fragment_id(p) for p in corpus_passages}
    document_ids = {canonical_document_id(p) for p in corpus_passages}
    all_ids, total = set(), 0
    for split in ("dev", "validation", "holdout"):
        questions, golds = _read_split(split)
        qids, gids = [q["id"] for q in questions], [g["id"] for g in golds]
        if len(qids) != len(set(qids)) or len(gids) != len(set(gids)) or set(qids) != set(gids):
            raise ValueError(f"Question/gold ID integrity failure: {split}")
        if all_ids & set(qids):
            raise ValueError("Split overlap detected")
        all_ids.update(qids)
        for q in questions:
            validator.validate(q)
            if FORBIDDEN_QUESTION_KEYS & q.keys():
                raise ValueError("Gold/evaluation field leaked into question input")
        for g in golds:
            validator.validate(g)
            if not set(g["gold_document_ids"]) <= document_ids or not set(g["gold_fragment_ids"]) <= fragment_ids:
                raise ValueError("Gold canonical ID does not resolve to corpus")
            for span in g["gold_spans"]:
                p = by_pid.get(span["passage_id"])
                if not p or canonical_fragment_id(p) != span["canonical_fragment_id"]:
                    raise ValueError("Gold span points to wrong passage/fragment")
                if not (p["clean_start"] <= span["clean_start"] < span["clean_end"] <= p["clean_end"]):
                    raise ValueError("Gold span is outside source passage")
        total += len(questions)
    manifest = read_json(BENCHMARK_ROOT / "manifests" / "benchmark_manifest.json")
    if manifest.get("schema_sha256") != file_hash(BENCHMARK_ROOT / "benchmark.schema.json"):
        raise ValueError("Benchmark schema hash differs from manifest")
    for split, expected in manifest.get("splits", {}).items():
        if expected.get("question_sha256") != file_hash(BENCHMARK_ROOT / "questions" / f"{split}.jsonl"):
            raise ValueError(f"Question split hash differs from manifest: {split}")
        if expected.get("gold_sha256") != file_hash(BENCHMARK_ROOT / "gold" / f"{split}.jsonl"):
            raise ValueError(f"Gold split hash differs from manifest: {split}")
    corpus_manifest = read_json(corpus / "manifest.json")
    for name, expected in manifest.get("corpus", {}).items():
        actual = corpus_manifest.get(name) if name in {"version", "bm25_sha256"} else corpus_manifest.get("hashes", {}).get(name)
        if actual != expected:
            raise ValueError(f"Corpus snapshot differs from benchmark manifest: {name}")
    if manifest["generation"]["target_total"] != total:
        raise ValueError("Manifest case count mismatch")
    return {"ok": True, "cases": total, "split_counts": {s: len(_read_split(s)[0]) for s in ("dev", "validation", "holdout")},
            "question_gold_separated": True, "gold_ids_resolved": True, "split_overlap": False,
            "manifest_sha256": file_hash(BENCHMARK_ROOT / "manifests" / "benchmark_manifest.json")}
