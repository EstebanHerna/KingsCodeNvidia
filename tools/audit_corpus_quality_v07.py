"""Read-only, preregistered source audit. Writes only reports/corpus_quality_v07.

This is an audit tool, not a corpus builder or retriever. It never downloads,
rewrites sources, or certifies legal currency. UNKNOWN is an explicit outcome.
"""
from pathlib import Path
import argparse
from collections import Counter, defaultdict
import io
import json
import random
import re
import sys
import unicodedata
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, file_hash, read_json, read_jsonl, write_json, write_jsonl
from kingscode.metadata import canonical_document_id, canonical_fragment_id, content_hash, temporal_status

OUT = ROOT / "reports/corpus_quality_v07"


def compact(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", text)).casefold()


def balanced(pool, n, key="doc_id"):
    rng = random.Random(0)
    groups = defaultdict(list)
    for row in sorted(pool, key=lambda x: x["passage_id"]):
        groups[row[key]].append(row)
    names = sorted(groups)
    rng.shuffle(names)
    for rows in groups.values(): rng.shuffle(rows)
    chosen = []
    while len(chosen) < n and any(groups.values()):
        for name in names:
            if groups[name] and len(chosen) < n:
                chosen.append(groups[name].pop())
    return chosen


def input_hashes(corpus):
    # Census before/after includes raw, clean, graph, manifests and all indexes.
    return {p.relative_to(corpus).as_posix(): file_hash(p)
            for p in sorted(corpus.rglob("*")) if p.is_file()}


def locate(corpus, stored_path):
    path = Path(stored_path)
    if path.parts[0] != "corpus":
        raise ValueError("Expected snapshot-relative corpus path")
    return corpus.joinpath(*path.parts[1:])


def sample(corpus):
    protocol = read_json(OUT / "audit_protocol.json")
    if (OUT / "audit_sample.jsonl").exists():
        raise FileExistsError("Sample is immutable; do not resample after seeing outcomes")
    ps = read_jsonl(corpus / "passages.jsonl")
    by_id = {p["passage_id"]: p for p in ps}
    before = input_hashes(corpus)
    write_json(OUT / "snapshot_hashes_before.json", before)
    error_report = read_json(ROOT / "reports/benchmark/error_analysis/r0_dev.json")
    run_dir = ROOT / error_report["run"]["directory"]
    rows = read_jsonl(run_dir / "per_question.jsonl")
    gold = {g["id"]: g for g in read_jsonl(ROOT / "benchmarks/kingscode_ir/gold/dev.jsonl")}
    risk = []
    associated = defaultdict(list)
    for row in sorted(rows, key=lambda r: r["id"]):
        if row["failure"] == "success": continue
        ids = [x["passage_id"] for x in gold[row["id"]].get("gold_spans", [])]
        ids += [x["passage_id"] for x in row["retrieved"]]
        for pid in dict.fromkeys(ids):
            associated[pid].append({"question_id": row["id"], "failure": row["failure"]})
            if pid in by_id:
                risk.append({**by_id[pid], "failure_category": row["failure"]})
    risk = list({p["passage_id"]: p for p in reversed(risk)}.values())
    pools = {
        "legislation": [p for p in ps if p["source_type"] == "law" and p["retrieval_eligible"]],
        "codes_decrees": [p for p in ps if p["source_type"] in {"code", "decree", "constitution"} and p["retrieval_eligible"]],
        "jurisprudence": [p for p in ps if p["source_type"] == "decision"],
        "historical": [p for p in ps if p["is_current_text"] is False],
        "ambiguous_excluded": [p for p in ps if not p["retrieval_eligible"] and p["is_current_text"] is not False],
        "benchmark_risk": risk,
    }
    units, counts = [], {}
    for stratum in protocol["strata"]:
        name = stratum["name"]
        chosen = balanced(pools[name], stratum["n"], "failure_category" if name == "benchmark_risk" else "doc_id")
        counts[name] = {"requested": stratum["n"], "pool": len(pools[name]), "sampled": len(chosen)}
        for p in chosen:
            units.append({"unit_id": f"{name}:{len(units)+1:03d}", "stratum": name,
                          "passage_id": p["passage_id"], "doc_id": p["doc_id"],
                          "source_url": p["source_url"], "benchmark_cases": associated.get(p["passage_id"], [])})
    write_jsonl(OUT / "audit_sample.jsonl", units)
    edges = read_jsonl(corpus / "graph/edges.jsonl")
    edge_groups = defaultdict(list)
    for e in edges: edge_groups[e["relation"]].append(e)
    edge_sample = []
    for relation, group in sorted(edge_groups.items()):
        group.sort(key=lambda e: (e["source"], e["target"], e["relation"], e["evidence_passage_id"]))
        random.Random(0).shuffle(group)
        edge_sample.extend(group[:20])
    write_jsonl(OUT / "graph_sample.jsonl", edge_sample)
    duplicate_slots = {pid: n for pid, n in Counter(u["passage_id"] for u in units).items() if n > 1}
    write_json(OUT / "sample_summary.json", {"protocol_sha256": file_hash(OUT / "audit_protocol.json"),
               "sample_sha256": file_hash(OUT / "audit_sample.jsonl"), "slots": len(units),
               "unique_passages": len({u["passage_id"] for u in units}),
               "unique_documents": len({u["doc_id"] for u in units}), "strata": counts,
               "overlaps": duplicate_slots, "graph_units": len(edge_sample),
               "graph_population": dict(Counter(e["relation"] for e in edges)),
               "r0_dev_report": str(run_dir.relative_to(ROOT)), "r0_dev_rows_sha256": file_hash(run_dir / "per_question.jsonl")})


def raw_text(data):
    if data.startswith(b"%PDF-"):
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages), "independent_pdf_text_layer"
    from bs4 import BeautifulSoup
    try: text = data.decode("utf-8-sig")
    except UnicodeDecodeError: text = data.decode("cp1252", errors="replace")
    soup = BeautifulSoup(text, "html.parser")
    for tag in soup.select("script,style"): tag.decompose()
    return soup.get_text(" ", strip=True), "independent_html_text_whitespace_normalized"


def outcome(value, evidence):
    return {"status": "UNKNOWN" if value is None else "PASS" if value else "FAIL", "evidence": evidence}


def inspect(corpus):
    protocol = read_json(OUT / "audit_protocol.json")
    before = read_json(OUT / "snapshot_hashes_before.json")
    if input_hashes(corpus) != before: raise ValueError("Snapshot changed after preregistration/sample")
    manifest = read_json(corpus / "manifest.json")
    docs = {d["doc_id"]: d for d in manifest["documentos"]}
    ps = read_jsonl(corpus / "passages.jsonl")
    by_id = {p["passage_id"]: p for p in ps}
    nodes = {n["node_id"]: n for n in read_jsonl(corpus / "graph/nodes.jsonl")}
    by_unit, by_fragment, by_content = defaultdict(list), defaultdict(list), defaultdict(list)
    for p in ps:
        by_unit[p["graph_node_ids"][1]].append(p)
        by_fragment[canonical_fragment_id(p)].append(p)
        by_content[content_hash(p)].append(p)
    caches, results = {}, []
    for unit in read_jsonl(OUT / "audit_sample.jsonl"):
        p, d = by_id[unit["passage_id"]], docs[unit["doc_id"]]
        if p["doc_id"] not in caches:
            raw = locate(corpus, d["raw_path"])
            text, method = raw_text(raw.read_bytes())
            clean = locate(corpus, d["clean_path"]).read_text(encoding="utf-8")
            caches[p["doc_id"]] = (text, compact(text), clean, method)
        raw, flat, clean, method = caches[p["doc_id"]]
        body = p["text"][len(p["text_prefix"]):]
        structural = by_unit[p["graph_node_ids"][1]]
        first = min(structural, key=lambda p: p["clean_start"])
        header = clean[first["clean_start"]: first["clean_start"]+250]
        source_ok = None
        number, year = d.get("norm_number"), d.get("year")
        if d["source_type"] == "decision":
            parts = re.match(r"([A-Za-z]+)-?(\d+)", str(d["canonical_body"][1]))
            if parts:
                pattern = parts[1].lower()+r"-?0*"+str(int(parts[2]))+r"(?:/|-|de)(?:"+str(year)+"|"+str(year)[-2:]+r")(?!\d)"
                source_ok = bool(re.search(pattern, flat[:15000])) or None
        elif number and year:
            source_ok = bool(re.search(r"(?:ley|decreto(?:ley)?|decision)0*"+re.escape(str(number).lstrip("0"))+r"(?:de|/|-)"+str(year), flat[:15000])) or None
        elif d["doc_id"] == "constitucion":
            source_ok = "constituciónpolítica" in flat[:15000] and "1991" in flat[:15000]
        if d["doc_id"] == "codigo_civil":
            source_ok = "ley84de1873" in flat[:15000]
        offset_ok = p["text"] == p["text_prefix"] + clean[p["clean_start"]:p["clean_end"]]
        raw_match = compact(body) in flat
        article = p.get("article")
        locator_ok = None
        if article:
            label = str(article).replace("transitorio_", "")
            match = re.search(r"art[ií]culo\s+(?:transitorio\s+)?(\d+(?:[.,]\d+)*(?:\s*[-–]\s*\d+)?(?:\s*[a-z](?=\s*[.:]))?)", header, re.I)
            if match:
                observed = re.sub(r"(?<=\d)o$", "", re.sub(r"\s+", "", match[1].lower())).replace(",", ".")
                locator_ok = observed == label.lower() if not p["duplicate_article_heading"] else None
        hierarchy = p["hierarchy_path"][1:-1]
        hierarchy_ok = all(compact(h) in flat for h in hierarchy)
        same_fragment = by_fragment[canonical_fragment_id(p)]
        distinct_units = {x["graph_node_ids"][1] for x in same_fragment}
        temporal = temporal_status(p)
        historical_marker = "TEXTO ANTERIOR" in clean[first["clean_start"]:max(x["clean_end"] for x in structural)].upper()
        assertion_ok = None if temporal["status_assertion"] == "unknown" else historical_marker
        provenance_ok = (file_hash(locate(corpus, d["raw_path"])) == d["source_sha256"] == p["source_sha256"]
                         and file_hash(locate(corpus, d["clean_path"])) == d["sha256"]
                         and bool(d.get("retrieved_at")) and d.get("http_status") == 200
                         and d.get("tls_verified") is True and p["source_url"] == d["source_url"])
        supported_nodes = all(n in nodes and nodes[n].get("doc_id") == p["doc_id"] for n in p["graph_node_ids"])
        checks = {
            "source_identity_accuracy": outcome(source_ok, {"url": d["source_url"], "raw_path": d["raw_path"], "raw_heading": raw[:1800]}),
            "text_fidelity_rate": outcome(True if raw_match and offset_ok else None, {"exact_clean_slice": offset_ok, "body_found_in_raw": raw_match, "method": method}),
            "parser_error_rate": outcome(None, "Semantic boundary completeness requires review; exact offsets alone do not prove absence of parser errors."),
            "truncation_rate": outcome(None, "A matching substring does not prove that raw source content was not omitted."),
            "contamination_rate": outcome(None, "Presence in official raw is not proof that a passage excludes navigation, editorial or quoted material."),
            "article_locator_accuracy": outcome(locator_ok, {"declared": article, "unit_heading": header, "ambiguous": p["duplicate_article_heading"]}),
            "hierarchy_accuracy": outcome(True if hierarchy_ok else None, {"declared": hierarchy, "scope": "literal source heading membership only; parent semantics not certified"}),
            "structural_metadata_accuracy": outcome(supported_nodes and offset_ok, {"node_identity_and_offsets_only": True}),
            "canonical_document_accuracy": outcome(source_ok, {"id": canonical_document_id(p), "scope": "declared identity corroboration; alias completeness reviewed separately"}),
            "canonical_fragment_accuracy": outcome(False if len(distinct_units) > 1 else (True if locator_ok else None), {"id": canonical_fragment_id(p), "structural_units": sorted(distinct_units)}),
            "provenance_complete_rate": outcome(provenance_ok, "Raw/clean hashes, URL equality, timestamp, TLS and HTTP status verified."),
            "verified_temporal_status_rate": outcome(assertion_ok, {"status": temporal, "publisher_historical_marker": historical_marker}),
            "incorrect_temporal_assertion_rate": outcome(assertion_ok, "UNKNOWN is excluded from asserted temporal status denominator."),
            "unknown_with_no_evidence_rate": outcome(temporal["status_assertion"] == "unknown", "Share of all sampled passages conservatively labelled unknown; not an error rate."),
        }
        if not article: checks["article_locator_accuracy"]["status"] = "NOT_APPLICABLE"
        results.append({**unit, "checks": checks, "clean_start": p["clean_start"], "clean_end": p["clean_end"],
                        "body_excerpt": body[:600], "canonical_document_id": canonical_document_id(p),
                        "canonical_fragment_id": canonical_fragment_id(p)})
    write_jsonl(OUT / "unit_checks.jsonl", results)
    collisions = []
    for fid, group in sorted(by_fragment.items()):
        units = {p["graph_node_ids"][1] for p in group}
        if len(units) > 1:
            collisions.append({"canonical_fragment_id": fid, "units": sorted(units),
                               "passage_ids": [p["passage_id"] for p in group],
                               "scope": "distinct structural occurrences; semantic distinctness requires evidence review"})
    write_json(OUT / "canonical_census.json", {"fragment_groups": len(by_fragment),
               "multi_segment_groups": sum(len(g)>1 for g in by_fragment.values()),
               "cross_structural_unit_candidates": collisions,
               "content_mirror_groups": [{"hash": h, "passage_ids": [p["passage_id"] for p in group],
                  "canonical_documents": sorted({canonical_document_id(p) for p in group})}
                   for h, group in sorted(by_content.items()) if len(group)>1],
               "note": "Long physical segments within the same unit are not collisions. Shared normalized text across different documents may be common boilerplate, not a mirror."})
    graph_checks = []
    for e in read_jsonl(OUT / "graph_sample.jsonl"):
        p = by_id.get(e["evidence_passage_id"])
        src, dst = nodes.get(e["source"]), nodes.get(e["target"])
        text_found = bool(p and e["evidence_text"] in p["text"])
        relation_ok = None
        if src and dst and text_found and e.get("method"):
            if e["relation"] == "CITA":
                relation_ok = bool(re.search(r"\b(?:Ley|Decreto)\s+(?:Ley\s+)?\d+\s+de\s+\d{4}", e["evidence_text"], re.I))
            elif e["relation"] in {"DEROGA", "MODIFICA"}:
                verb = "derogad" if e["relation"] == "DEROGA" else "modificad"
                relation_ok = bool(re.search(verb+r"[oa]\s+por\b", e["evidence_text"], re.I))
            elif e["relation"] == "REMITE_A":
                m = re.search(r"art[ií]culo\s+(\d+[A-Za-z]?)", e["evidence_text"], re.I)
                relation_ok = bool(m and dst.get("article") == m[1].lower() and src.get("doc_id") == dst.get("doc_id"))
            elif e["relation"] == "CONTIENE":
                relation_ok = bool(src.get("doc_id") == dst.get("doc_id") == p["doc_id"])
        graph_checks.append({**e, "source_node": src, "target_node": dst,
                             "evidence_text_present": text_found,
                             "mechanical_grounding": outcome(relation_ok, "Endpoints/provenance and explicit lexical relation; legal attachment reviewed separately."),
                             "semantic_grounding": {"status": "UNKNOWN", "evidence": "Requires context review, not just lexical coexistence."},
                             "context": p["text"] if p else None})
    write_jsonl(OUT / "graph_checks.jsonl", graph_checks)
    backlog = read_json(ROOT / "reports/acquisition_backlog_v06.json")
    acquisition = {d["doc_id"]: d for d in read_json(corpus / "acquisition.json")["documents"]}
    write_json(OUT / "target_review.json", {"targets": [{"original": t,
               "acquisition_record": acquisition.get(t["doc_id"]),
               "official_sources_attempted": [t.get("seed_url")],
               "source_attempt_note": "Seed search URL is recorded separately from actual resolved attempts; inspect acquisition error/discovery cache.",
               "new_evidence": [], "current_status": t["resolution"], "verification": "UNVERIFIED; identifier preserved"}
               for t in backlog["targets"]]})
    after = input_hashes(corpus)
    write_json(OUT / "snapshot_hashes_after.json", after)
    if after != before: raise ValueError("Audit changed snapshot or snapshot was modified concurrently")
    print(json.dumps({"units": len(results), "graph_units": len(graph_checks),
                      "collision_candidates": len(collisions), "snapshot_unchanged": True}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["sample", "inspect"])
    parser.add_argument("--corpus", type=Path, required=True)
    args = parser.parse_args()
    (sample if args.phase == "sample" else inspect)(args.corpus.resolve())
