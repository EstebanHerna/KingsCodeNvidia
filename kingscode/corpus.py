"""Extract official text, structural passages and evidence-backed graph together."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
from urllib.parse import urlparse
from bs4 import Comment, NavigableString

from .acquisition import soup_from_bytes
from .common import ROOT, VERSION, digest, file_hash, indexable, normalize, read_json, slug, write_json, write_jsonl

PARSER_VERSION = "legal-blocks-1.2"
ARTICLE = re.compile(r"^art[ií]culo\s+(?:(transitorio)\s+)?(\d+(?:\s*[.,]\s*\d+)*(?:\s*[-–]\s*\d+)?(?:[A-Za-z]|\s+[A-Za-z](?=\s*[.:]))?)(?=[\s.°ºº:ª])", re.I)
HEADING = re.compile(r"^(LIBRO|PARTE|T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N)\s+([IVXLC\d]+|PRELIMINAR|[ÚU]NICO|PRIMER[OA]|SEGUND[OA]|TERCER[OA]|CUART[OA]|TRANSITORIO)\b", re.I)
PARAGRAPH = re.compile(r"^PAR[ÁA]GRAFO\s*(?:(TRANSITORIO)\s*)?(\d+)?", re.I)
CLAUSE = re.compile(r"^(\d+|[a-z])[.)]\s+", re.I)
NORM_REF = re.compile(r"\b(Ley|Decreto(?:\s+Ley)?)\s+(\d{1,5})\s+de\s+(\d{4})\b", re.I)
SELF_REF = re.compile(r"\bart[ií]culo\s+(\d+[A-Za-z]?)\s+de(?:l\s+presente|\s+este|\s+esta|\s+la\s+presente)\s+(?:c[oó]digo|ley|decreto|constituci[oó]n)\b", re.I)


class SourceBlock(str):
    def __new__(cls, text, anchored=False, page=None):
        obj = str.__new__(cls, text)
        obj.anchored = anchored
        obj.page = page
        return obj


def blocks_from_pdf(data: bytes, skip_pages=()) -> tuple[list[str], str]:
    import io
    import pdfplumber
    blocks = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            if page_num in skip_pages:
                continue
            text = page.extract_text() or ""
            if len(text.strip()) < 50:
                raise ValueError(f"PDF page {page_num} needs OCR; refusing partial ingestion")
            pending = []
            for line in text.splitlines():
                line = re.sub(r"\s+", " ", line).strip()
                if re.match(r"^(?:SCLAJPT-|Radicación n\.|\d+$|-\s*\d+\s*-$)", line):
                    continue
                heading = ARTICLE.match(line) or HEADING.match(line) or re.match(r"^[IVX]+\.\s+[A-ZÁÉÍÓÚÑ ]+$", line)
                if heading and pending:
                    blocks.append(SourceBlock(" ".join(pending), page=page_num))
                    pending = []
                pending.append(line)
            if pending:
                blocks.append(SourceBlock(" ".join(pending), page=page_num))
    return blocks, "PDF text layer; layout checked on acquisition"


def blocks_from_html(data: bytes, decision: bool = False) -> tuple[list[str], str]:
    soup = soup_from_bytes(data)
    container = soup.select_one(".descripcion-contenido") or soup.select_one(".panel-documento")
    if container is None and decision:
        container = soup.select_one("article") or soup.body
    if container is None:
        raise ValueError("Missing official document container")
    for tag in container.select("script, style, nav, header, footer, form, button"):
        tag.decompose()
    # Publisher's collapsed historical/editorial panels are preserved in raw,
    # but not mixed with the consolidated legal text. Court decisions sometimes
    # use hidden Word spans; this rule only targets normative source panels.
    if not decision:
        for tag in list(container.select("[style], .caja_vja_c, .caja_vja_v, .caja_vja_la, .ir-arriba")):
            if tag.attrs is not None and (re.search(r"display\s*:\s*none", tag.get("style", ""), re.I)
                                         or any(c.startswith("caja_vja_") for c in tag.get("class", []))
                                         or "ir-arriba" in tag.get("class", [])):
                tag.decompose()
    blocks, buffer = [], []
    anchored = False

    def flush():
        nonlocal anchored
        text = re.sub(r"\s+", " ", " ".join(buffer)).strip()
        if text:
            blocks.append(SourceBlock(text, anchored))
        buffer.clear()
        anchored = False

    def walk(tag):
        nonlocal anchored
        if isinstance(tag, Comment):
            return
        if isinstance(tag, NavigableString):
            buffer.append(str(tag))
            return
        boundary = tag.name in {"p", "div", "h1", "h2", "h3", "h4", "li", "td", "tr", "br"}
        if boundary:
            flush()
        if tag.name == "a" and re.fullmatch(r"(?:sp|BM)?\d+[A-Za-z]?", tag.get("id", tag.get("name", ""))):
            anchored = True
        for child in tag.children:
            walk(child)
        if boundary:
            flush()

    walk(container)
    flush()
    if len(blocks) < 3:
        raise ValueError("Insufficient structural text blocks")
    return blocks, soup.title.get_text(" ", strip=True) if soup.title else ""


def block_offsets(blocks: list[str]) -> list[tuple[int, int]]:
    result, start = [], 0
    for b in blocks:
        result.append((start, start + len(b)))
        start += len(b) + 2
    return result


def segments(text: str, start: int, end: int, target: int = 2400, maximum: int = 3600):
    """Contiguous exact slices, preferring paragraphs then sentence boundaries."""
    while end - start > maximum:
        cut = text.rfind("\n\n", start + target // 2, start + maximum)
        if cut < start:
            marks = list(re.finditer(r"[.;!?]\s+(?=[A-ZÁÉÍÓÚÑ¿])", text[start + target // 2:start + maximum]))
            cut = start + target // 2 + marks[-1].end() if marks else text.rfind(" ", start + 1, start + maximum)
        if cut <= start:
            cut = start + maximum
        while cut > start and text[cut - 1].isspace():
            cut -= 1
        yield start, cut
        start = cut
        while start < end and text[start].isspace():
            start += 1
    if text[start:end].strip():
        while end > start and text[end - 1].isspace():
            end -= 1
        yield start, end


def parse_document(meta: dict, data: bytes) -> tuple[str, list[dict], list[dict], list[dict], dict]:
    decision = meta["source_type"] == "decision"
    blocks, title = blocks_from_pdf(data, meta.get("pdf_skip_pages", [])) if data.startswith(b"%PDF-") else blocks_from_html(data, decision)
    clean = "\n\n".join(blocks)
    offsets = block_offsets(blocks)
    doc_id = meta["doc_id"]
    doc_node = f"doc:{doc_id}"
    nodes = [{"node_id": doc_node, "node_type": "DECISION" if decision else "NORM",
              "label": meta["norm_name"], "doc_id": doc_id, "resolved": True}]
    edges, passages, units = [], [], []
    section_nodes = set()
    hierarchy = []
    counts = Counter()
    active = None
    heading_rank = {"libro": 0, "parte": 1, "titulo": 2, "capitulo": 3, "seccion": 4}
    transitory = False
    for i, b in enumerate(blocks):
        hm = HEADING.match(b)
        if hm and len(b) < 220:
            rank = heading_rank[normalize(hm.group(1))]
            hierarchy = [h for h in hierarchy if h[0] < rank] + [(rank, b)]
            if "transitori" in normalize(b):
                transitory = True
        am = None if decision else ARTICLE.match(b)
        if am and data.startswith(b"%PDF-") and not re.match(r"^Art[ií]culo\s+\d+\s*[.]?\s*[-–]", b):
            # The CAN PDF wraps lowercase in-sentence references at page/line
            # boundaries. Actual article headings use "Artículo N.-".
            am = None
        prior = " ".join(blocks[max(0, i - 3):i])
        if am and re.search(r"quedar[aá]n?\s+as[ií]\s*[:.]?\s*$", prior, re.I):
            am = None
        if am and active and active.get("amendment"):
            candidate = re.sub(r"\s+", "", am.group(2)).lower().rstrip("o")
            # A replacing law can quote a whole title (many articles). Keep that
            # text under the enacting article until its own sequence resumes.
            if active["article"].isdigit() and candidate != str(int(active["article"]) + 1):
                am = None
        # Long quoted amendments inside an article are content, not top-level articles.
        if am:
            article = re.sub(r"\s+", "", am.group(2)).lower().replace(",", ".")
            article = re.sub(r"(?<=\d)o$", "", article)  # 1o. is an ordinal, not article 1-O
            if am.group(1) or transitory:
                article = "transitorio_" + article
            if active:
                active["end"] = offsets[i][0]
            counts[article] += 1
            unit_id = f"{doc_node}:article:{article}:v{counts[article]}"
            active = {"start": offsets[i][0], "end": len(clean), "article": article,
                      "unit_id": unit_id, "hierarchy": [h[1] for h in hierarchy],
                      "heading": b[:min(len(b), 180)], "first_block": i,
                      "duplicate": counts[article] > 1,
                      "amendment": bool(re.search(r"\b(modifiquese|modifiquense|adicionese|adicionense|sustituyase|sustituyanse)\b", normalize(b[:500]))
                                        and "asi" in normalize(b))}
            units.append(active)
    if not units:
        if not decision:
            raise ValueError("No article headings: refusing an unstructured statute")
        # Section titles are only taken from source. Never infer a ratio/holding.
        boundaries = [0]
        for i, b in enumerate(blocks):
            if i and len(b) < 160 and re.match(r"^(?:[IVX]+[. -]+)?(?:ANTECEDENTES|CONSIDERACIONES|FUNDAMENTOS|DECISI[ÓO]N|RESUELVE|PROBLEMA JUR[IÍ]DICO)", b, re.I):
                boundaries.append(i)
        boundaries.append(len(blocks))
        for n, (a, z) in enumerate(zip(boundaries, boundaries[1:])):
            units.append({"start": offsets[a][0], "end": offsets[z][0] if z < len(blocks) else len(clean),
                          "article": None, "unit_id": f"{doc_node}:section:{n}",
                          "hierarchy": [blocks[a][:150] if a else "Texto de la providencia"],
                          "heading": blocks[a][:150], "first_block": a, "duplicate": False})
    for u in units:
        unit_node = u["unit_id"]
        nodes.append({"node_id": unit_node, "node_type": "SECTION" if decision else "ARTICLE",
                      "label": u["heading"], "doc_id": doc_id, "article": u["article"], "resolved": True})
        # Historical text explicitly marked by publisher is isolated and excluded
        # from default indexes, while retained in clean/raw for audit.
        historical = re.search(r"\bTEXTO\s+ANTERIOR\s*:", clean[u["start"]:u["end"]], re.I)
        hist_start = u["start"] + historical.start() if historical else None
        ranges = [(u["start"], hist_start or u["end"], None)]
        if hist_start is not None:
            ranges.append((hist_start, u["end"], False))
        created = []
        for begin, finish, current in ranges:
            for a, z in segments(clean, begin, finish):
                order = len(passages)
                pid = f"{doc_id}:{order:05d}:{digest(clean[a:z].encode())[:12]}"
                header = meta["norm_name"] + "."
                if u["hierarchy"]:
                    header += "\n" + "\n".join(u["hierarchy"])
                if u["article"] and a != u["start"]:
                    header += " Artículo " + u["article"] + " (continuación)."
                text = header + "\n" + clean[a:z]
                p = {"passage_id": pid, "doc_id": doc_id, "source_type": meta["source_type"],
                     "title": meta["norm_name"], "norm_name": meta["norm_name"],
                     "norm_number": meta["norm_number"], "year": meta["year"],
                     "canonical_body": meta["canonical_body"],
                     "court": "Corte Constitucional" if decision else None,
                     "decision_id": meta["canonical_body"][1] if decision else None,
                     "article": u["article"], "paragraph": None, "clause": None,
                     "section": u["hierarchy"][-1] if u["hierarchy"] else None,
                     "hierarchy_path": [meta["norm_name"], *u["hierarchy"], u["heading"]],
                     "text": text, "source_url": meta["source_url"],
                     "source_domain": urlparse(meta["source_url"]).hostname,
                     "source_sha256": meta["source_sha256"], "retrieved_at": meta["retrieved_at"],
                     "areas": meta["areas"], "tags": [], "graph_node_ids": [doc_node, unit_node],
                     "order_index": order, "clean_start": a, "clean_end": z,
                     "text_prefix": header + "\n", "offset_basis": "unicode_codepoints_in_clean_text",
                     "is_current_text": current,
                     "notes": "Vigencia no certificada; conservar notas de la fuente.",
                     "duplicate_article_heading": u["duplicate"]}
                passages.append(p)
                if data.startswith(b"%PDF-"):
                    p["source_pages"] = sorted({b.page for b, (x, y) in zip(blocks, offsets) if x < z and y > a})
                    p["court"] = meta.get("court")
                created.append(p)
        if not created:
            continue
        parent_section = doc_node
        section_path = []
        if not decision:
            for heading in u["hierarchy"]:
                section_path.append(heading)
                section_id = f"{doc_node}:heading:{digest('/'.join(section_path).encode())[:16]}"
                if section_id not in section_nodes:
                    nodes.append({"node_id": section_id, "node_type": "SECTION", "label": heading,
                                  "doc_id": doc_id, "resolved": True})
                    edges.append({"source": parent_section, "target": section_id, "relation": "CONTIENE",
                                  "evidence_passage_id": created[0]["passage_id"], "evidence_text": heading,
                                  "method": "source_hierarchy"})
                    section_nodes.add(section_id)
                parent_section = section_id
                # Do not put broad section nodes into graph_node_ids: expansion
                # remains local and hierarchy stays available through edges.
        edges.append({"source": parent_section, "target": unit_node, "relation": "CONTIENE",
                      "evidence_passage_id": created[0]["passage_id"], "evidence_text": u["heading"],
                      "method": "source_structure"})
        # Paragraphs and numbered clauses preserve structural location, without
        # duplicating their text into additional retrieval candidates.
        parent = unit_node
        for i, b in enumerate(blocks):
            a, z = offsets[i]
            if a < u["start"] or a >= u["end"]:
                continue
            pm, cm = PARAGRAPH.match(b), CLAUSE.match(b)
            if not pm and not cm:
                continue
            nt = "PARAGRAPH" if pm else "CLAUSE"
            node_id = f"{unit_node}:{nt.lower()}:{i}"
            nodes.append({"node_id": node_id, "node_type": nt, "label": b[:100],
                          "doc_id": doc_id, "clean_start": a, "clean_end": z, "resolved": True})
            associated = [p for p in created if p["clean_start"] < z and p["clean_end"] > a]
            for p in associated:
                p["graph_node_ids"].append(node_id)
            if associated:
                edges.append({"source": unit_node if pm else parent, "target": node_id,
                              "relation": "CONTIENE", "evidence_passage_id": associated[0]["passage_id"],
                              "evidence_text": b[:100], "method": "source_structure"})
            if pm:
                parent = node_id
    # Repeated article numbers may be quoted annexes, publisher histories or
    # distinct transitional titles. Do not guess which occurrence is canonical.
    # Retain all source text/graph for audit, but exclude the entire ambiguous
    # article group until its scope can be resolved from reliable metadata.
    for p in passages:
        ambiguous = counts[p["article"]] > 1 if p["article"] is not None else False
        p["duplicate_article_heading"] = ambiguous
        reasons = (["ambiguous_article_number"] if ambiguous else []) + (["historical_text"] if p["is_current_text"] is False else [])
        p["index_exclusion_reasons"] = reasons
        p["retrieval_eligible"] = not reasons
    info = {"source_title": title, "n_articulos": len(counts) if not decision else None,
            "duplicate_headings": {k: v for k, v in counts.items() if v > 1},
            "n_fragmentos": len(passages), "n_historical_fragments": sum(p["is_current_text"] is False for p in passages),
            "n_ambiguous_fragments": sum(p["duplicate_article_heading"] for p in passages),
            "n_indexed": sum(indexable(p) for p in passages)}
    return clean, passages, nodes, edges, info


def link_references(passages: list[dict], nodes: list[dict], edges: list[dict], documents: list[dict]):
    norms = {}
    for doc in documents:
        body = doc["canonical_body"]
        if body[0] in {"ley", "decreto"}:
            norms[(body[0], body[1], str(body[2]))] = f"doc:{doc['doc_id']}"
        elif doc["norm_number"]:
            kind = "decreto" if "decreto" in normalize(doc["norm_name"]) else "ley"
            norms[(kind, doc["norm_number"], str(doc["year"]))] = f"doc:{doc['doc_id']}"
    node_ids = {n["node_id"] for n in nodes}
    article_counts = Counter((n["doc_id"], n.get("article")) for n in nodes if n["node_type"] == "ARTICLE")
    articles = {(n["doc_id"], n.get("article")): n["node_id"] for n in nodes
                if n["node_type"] == "ARTICLE" and article_counts[(n["doc_id"], n.get("article"))] == 1}
    seen = set()
    for p in passages:
        if not indexable(p):
            continue
        source = p["graph_node_ids"][1]
        body = p["text"][len(p["text_prefix"]):]
        for m in NORM_REF.finditer(body):
            kind = "decreto" if normalize(m[1]).startswith("decreto") else "ley"
            key = (kind, str(int(m[2])), m[3])
            target = norms.get(key, f"external:{kind}:{key[1]}:{key[2]}")
            if target == p["graph_node_ids"][0]:
                continue
            if target not in node_ids:
                nodes.append({"node_id": target, "node_type": "NORM", "label": m[0],
                              "doc_id": None, "resolved": False})
                node_ids.add(target)
            relation, src, dst = "CITA", source, target
            # Conservative passive form: publisher explicitly says this unit was
            # modified/repealed by the cited norm. Never reverse its direction.
            before = body[max(0, m.start() - 120):m.start()]
            passive = re.search(r"(?i)(modificado|modificada|derogado|derogada)\s+por\s+(?:el\s+)?(?:art[ií]culo\s+\d+\s+de\s+)?(?:la\s+|el\s+)?$", before)
            evidence = m[0]
            if passive:
                relation = "MODIFICA" if normalize(passive[1]).startswith("modific") else "DEROGA"
                src, dst = target, source
                evidence = before[passive.start():] + m[0]
            edge_key = (src, dst, relation, p["passage_id"])
            if edge_key not in seen:
                edges.append({"source": src, "target": dst, "relation": relation,
                              "evidence_passage_id": p["passage_id"], "evidence_text": evidence,
                              "method": "explicit_text_reference"})
                seen.add(edge_key)
        for m in SELF_REF.finditer(body):
            target = articles.get((p["doc_id"], m[1].lower()))
            key = (source, target, "REMITE_A", p["passage_id"])
            if target and target != source and key not in seen:
                edges.append({"source": source, "target": target, "relation": "REMITE_A",
                              "evidence_passage_id": p["passage_id"], "evidence_text": m[0],
                              "method": "explicit_same_document_reference"})
                seen.add(key)


def build(out: Path) -> dict:
    acquisition = read_json(out / "acquisition.json")
    documents, failures, passages, nodes, edges = [], [], [], [], []
    (out / "clean").mkdir(parents=True, exist_ok=True)
    for meta in sorted(acquisition["documents"], key=lambda d: d["doc_id"]):
        if meta["status"] != "downloaded":
            failures.append({"doc_id": meta["doc_id"], "stage": "download", "error": meta["error"]})
            continue
        raw = ROOT / meta["raw_path"]
        if file_hash(raw) != meta["source_sha256"]:
            raise ValueError(f"Raw hash mismatch: {raw}")
        try:
            clean, ps, ns, es, info = parse_document(meta, raw.read_bytes())
        except ValueError as exc:
            failures.append({"doc_id": meta["doc_id"], "stage": "parse", "error": str(exc)})
            continue
        path = out / "clean" / f"{meta['doc_id']}.txt"
        path.write_text(clean, encoding="utf-8", newline="\n")
        documents.append({**meta, **info, "status": "parsed", "clean_path": path.relative_to(ROOT).as_posix(),
                          "sha256": file_hash(path), "titulo": meta["norm_name"],
                          "fuente": meta.get("institution") or ("Función Pública" if "funcionpublica" in meta["source_url"] else "SENA" if "sena.edu.co" in meta["source_url"] else "Corte Constitucional"),
                          "url": meta["source_url"], "fecha_consulta": meta["retrieved_at"][:10],
                          "metodo_ingesta": PARSER_VERSION})
        passages.extend(ps)
        nodes.extend(ns)
        edges.extend(es)
    if not passages:
        raise ValueError("No valid documents: refusing to overwrite corpus with empty index")
    link_references(passages, nodes, edges, documents)
    write_jsonl(out / "passages.jsonl", passages)
    write_jsonl(out / "graph/nodes.jsonl", sorted(nodes, key=lambda n: n["node_id"]))
    write_jsonl(out / "graph/edges.jsonl", sorted(edges, key=lambda e: (e["source"], e["target"], e["relation"], e["evidence_passage_id"])))
    hashes = {p: file_hash(out / p) for p in ["passages.jsonl", "graph/nodes.jsonl", "graph/edges.jsonl"]}
    from .retrieval import BM25Index
    index = BM25Index([p for p in passages if indexable(p)])
    index.save(out / "index/bm25.json", hashes["passages.jsonl"])
    manifest = {"equipo": "KingsCode", "version": VERSION, "parser_version": PARSER_VERSION,
                "licencia": "Pendiente de ratificación del equipo para el procesamiento propio",
                "enlace_nube": None, "encoder": None, "dimension": None, "indice": "BM25 inverted index",
                "n_documentos": len(documents), "n_fragmentos": len(passages), "n_indexed": len(index.passages),
                "n_nodes": len(nodes), "n_edges": len(edges), "hashes": hashes,
                "bm25_sha256": file_hash(out / "index/bm25.json"),
                "documentos": documents, "failures": failures,
                "provenance_policy": "official raw bytes only; sample/answers never used in build or index",
                "currency_policy": "source snapshot, not a certification of legal validity; historical and ambiguous article groups excluded"}
    write_json(out / "manifest.json", manifest)
    if out.resolve() == (ROOT / "corpus").resolve():
        write_json(ROOT / "corpus_manifest.json", manifest)
    return {k: manifest[k] for k in ["version", "n_documentos", "n_fragmentos", "n_indexed", "n_nodes", "n_edges", "hashes"]} | {"failures": len(failures)}
