"""Canonical legal identity and v0.6 metadata derivation (Phases 2, 3, 4).

This module is a pure, deterministic derivation layer on top of the Corpus v0.1
passage/document records. It does NOT re-parse sources, download anything, or read
evaluation labels. Given a passage or document it computes:

- ``canonical_document_id``  stable id for the legal work, independent of URL.
- ``canonical_fragment_id``  stable id for the article/section within the work.
- a ``document_metadata`` view (issuing body, official source, temporal fields).
- a ``passage_metadata`` view (structural locator + ``content_hash``).

Design rules honoured here:
- Same legal reference -> same canonical ID (URL/source mirror independent).
- Document and fragment IDs are separate namespaces.
- Genuinely distinct historical variants stay distinct (the ambiguous-article
  marker is folded into the fragment id so mirrored duplicates collapse but real
  variants do not).
- Legal validity is never inferred: temporal/status fields default to ``unknown``
  / ``null`` unless the corpus already carries explicit evidence.
- No arbitrary authority score is produced.
- Technical provenance (hashes, URLs, HTTP status, paths, timestamps) is kept in
  the document/passage metadata views and NEVER injected into embedding text.
"""
from __future__ import annotations

import re

from .common import digest, normalize, slug

METADATA_VERSION = "metadata-v0.6"

_TEMPORAL_STATES = {"current", "historical", "repealed", "modified", "unknown"}

# Canonical short names for the few foundational codes whose canonical id reads
# better as a code alias than as its enacting law/decree number. These are exact,
# well-known identities from the acquisition OVERRIDES, not guesses.
_CODE_ALIASES = {
    "codigo_civil": "codigo_civil",
    "codigo_comercio": "codigo_comercio",
    "codigo_penal": "codigo_penal",
    "codigo_general_proceso": "codigo_general_proceso",
    "codigo_sustantivo_trabajo": "codigo_sustantivo_trabajo",
    "estatuto_tributario": "estatuto_tributario",
    "constitucion": "constitucion",
}


def _decision_slug(number: str) -> tuple[str, str]:
    """Split a decision identifier like ``C-355`` into (sala, sequence)."""
    m = re.match(r"^([A-Za-z]+)-?(\w+)$", number or "")
    if not m:
        return ("", slug(number or ""))
    return (m.group(1).lower(), m.group(2).lower())


def canonical_document_id(record: dict) -> str:
    """Deterministic canonical id for the legal work of a passage/document.

    Independent of ``source_url``. Examples::

        ley:1564:2012
        decreto:410:1971
        codigo_civil
        corte_constitucional:c355:2006
    """
    body = record.get("canonical_body") or []
    kind = (body[0] if body else record.get("source_type")) or "other"
    number = body[1] if len(body) > 1 else record.get("norm_number")
    year = body[2] if len(body) > 2 else record.get("year")
    doc_id = record.get("doc_id", "")

    if kind in {"constitucion", "constitution"}:
        y = year or "1991"
        return f"constitucion:{y}"
    if kind == "jurisprudencia" or record.get("source_type") == "decision":
        sala, seq = _decision_slug(str(number or record.get("decision_id") or ""))
        court = "corte_constitucional" if sala in {"c", "t", "su"} else "corte_suprema"
        return f"{court}:{sala}{seq}:{year}" if sala else f"{court}:{slug(str(number))}:{year}"
    if kind in {"ley", "law"} and number:
        return f"ley:{str(number).lstrip('0') or number}:{year}"
    if kind in {"decreto", "decree"} and number:
        return f"decreto:{str(number).lstrip('0') or number}:{year}"
    if kind == "code" or record.get("source_type") == "code":
        alias = _CODE_ALIASES.get(doc_id)
        if alias:
            return alias
        if number and year:
            return f"decreto:{str(number).lstrip('0') or number}:{year}"
    # Fall back to a stable slug of the declared identity, never the URL.
    return f"{slug(str(kind))}:{slug(str(number))}:{year}" if number else slug(doc_id or record.get("norm_name", ""))


def _locator_slug(passage: dict) -> str:
    """Stable slug of the structural locator inside a document."""
    article = passage.get("article")
    if article:
        return "articulo:" + normalize(str(article)).replace(" ", "")
    section = passage.get("section")
    if section:
        return "seccion:" + digest(normalize(section).encode())[:12]
    return "orden:" + f"{passage.get('order_index', 0):06d}"


def canonical_fragment_id(passage: dict) -> str:
    """Deterministic canonical id for a fragment within its legal work.

    Separate namespace from the document id. Examples::

        ley:1564:2012:articulo:391
        codigo_civil:articulo:1602
        corte_constitucional:c355:2006:seccion:<hash>

    Genuinely distinct historical variants are kept distinct: when the corpus
    marks a fragment as a duplicate/ambiguous article heading or as historical
    text, that state is folded into the id so mirrored copies collapse while real
    variants remain separate.
    """
    doc = canonical_document_id(passage)
    base = f"{doc}:{_locator_slug(passage)}"
    variant = []
    if passage.get("is_current_text") is False:
        variant.append("historico")
    if passage.get("duplicate_article_heading"):
        # A repeated article heading is a genuinely distinct occurrence; keep it
        # distinct by its order so we never merge two different texts.
        variant.append(f"var{passage.get('order_index', 0):06d}")
    return base + (":" + ":".join(variant) if variant else "")


def content_hash(passage: dict) -> str:
    """Hash of the semantic body only (excludes the norm/hierarchy text_prefix).

    Two official mirrors of the same fragment yield the same ``content_hash`` so
    duplicates can be grouped, while the hash never enters embedding text.
    """
    prefix = passage.get("text_prefix", "")
    text = passage.get("text", "")
    body = text[len(prefix):] if prefix and text.startswith(prefix) else text
    return "sha256:" + digest(normalize(body).encode())


def temporal_status(record: dict) -> dict:
    """Conservative temporal/status view. Never asserts validity without evidence.

    ``is_current_text`` in the corpus is a source-snapshot marker: ``False`` means
    the publisher explicitly flagged the block as prior text; ``None`` means not
    certified. We map that to a status assertion, defaulting to ``unknown``.
    """
    is_current = record.get("is_current_text")
    if is_current is False:
        status = "historical"
        status_source = record.get("passage_id")
        note = "Publisher explicitly marked this block as prior/historical text."
    else:
        status = "unknown"
        status_source = None
        note = "Temporal validity not certified by the source snapshot."
    return {"status_assertion": status,
            "status_source_passage_id": status_source,
            "effective_from": None,
            "effective_to": None,
            "version_date": None,
            "temporal_note": note}


def document_metadata(record: dict) -> dict:
    """Document-level metadata view (may carry technical provenance)."""
    body = record.get("canonical_body") or []
    number = body[1] if len(body) > 1 else record.get("norm_number")
    year = body[2] if len(body) > 2 else record.get("year")
    temporal = temporal_status(record)
    return {"doc_id": record.get("doc_id"),
            "canonical_document_id": canonical_document_id(record),
            "title": record.get("title") or record.get("norm_name"),
            "source_type": record.get("source_type"),
            "norm_number": number,
            "year": year,
            "issuing_body": record.get("court") or record.get("canonical_body", [None])[0],
            "official_source": record.get("source_url"),
            "source_url": record.get("source_url"),
            "source_sha256": record.get("source_sha256"),
            "retrieved_at": record.get("retrieved_at"),
            "version_date": temporal["version_date"],
            "effective_from": temporal["effective_from"],
            "effective_to": temporal["effective_to"],
            "status_assertion": temporal["status_assertion"],
            "status_source_passage_id": temporal["status_source_passage_id"]}


def passage_metadata(passage: dict) -> dict:
    """Passage-level metadata view. ``content_hash`` is technical, not embedded."""
    return {"passage_id": passage.get("passage_id"),
            "canonical_fragment_id": canonical_fragment_id(passage),
            "canonical_document_id": canonical_document_id(passage),
            "doc_id": passage.get("doc_id"),
            "article": passage.get("article"),
            "paragraph": passage.get("paragraph"),
            "clause": passage.get("clause"),
            "section": passage.get("section"),
            "hierarchy_path": passage.get("hierarchy_path", []),
            "order_index": passage.get("order_index"),
            "graph_node_ids": passage.get("graph_node_ids", []),
            "retrieval_eligible": passage.get("retrieval_eligible", True),
            "content_hash": content_hash(passage)}


def embedding_representation(passage: dict) -> str:
    """Experimental semantic representation for embedding (Phase 7).

    Produces a compact legal header (norm, number/year, article, título/capítulo)
    followed by the literal legal text. Deliberately excludes ALL technical
    provenance: sha256, raw_path, HTTP status, byte counts and retrieved_at never
    appear. This is an EXPERIMENT, not a replacement for the current ``text``
    representation, until it is measured on the target GPU.
    """
    lines: list[str] = []
    norm = passage.get("norm_name") or passage.get("title")
    if norm:
        lines.append(f"Norma: {norm}")
    body = passage.get("canonical_body") or []
    number = body[1] if len(body) > 1 else passage.get("norm_number")
    year = body[2] if len(body) > 2 else passage.get("year")
    kind = body[0] if body else passage.get("source_type")
    if passage.get("source_type") == "decision":
        did = passage.get("decision_id") or (body[1] if len(body) > 1 else None)
        if did:
            lines.append(f"Sentencia {did}" + (f" de {year}" if year else ""))
    elif number and year:
        label = "Decreto" if str(kind).startswith("decreto") or kind == "decree" else "Ley"
        lines.append(f"{label} {number} de {year}")
    if passage.get("article"):
        lines.append(f"Artículo {passage['article']}")
    # Título / Capítulo from the structural hierarchy, skipping the norm name.
    hierarchy = [h for h in (passage.get("hierarchy_path") or []) if h and h != norm]
    for h in hierarchy:
        if re.match(r"^(LIBRO|PARTE|T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N)\b", h, re.I):
            lines.append(h.strip())
    prefix = passage.get("text_prefix", "")
    text = passage.get("text", "")
    legal_text = text[len(prefix):] if prefix and text.startswith(prefix) else text
    header = "\n".join(dict.fromkeys(lines))  # dedupe, keep order
    return (header + "\n\n" + legal_text).strip() if header else legal_text.strip()


def enrich_passage(passage: dict) -> dict:
    """Return a copy of ``passage`` with v0.6 canonical/temporal fields attached.

    Backward compatible: only adds fields (schema allows additionalProperties).
    Does not touch ``text`` and therefore never changes embedding content.
    """
    out = dict(passage)
    out["canonical_document_id"] = canonical_document_id(passage)
    out["canonical_fragment_id"] = canonical_fragment_id(passage)
    out["content_hash"] = content_hash(passage)
    out["metadata_version"] = METADATA_VERSION
    temporal = temporal_status(passage)
    out["status_assertion"] = temporal["status_assertion"]
    out["status_source_passage_id"] = temporal["status_source_passage_id"]
    out["effective_from"] = temporal["effective_from"]
    out["effective_to"] = temporal["effective_to"]
    out["version_date"] = temporal["version_date"]
    return out
