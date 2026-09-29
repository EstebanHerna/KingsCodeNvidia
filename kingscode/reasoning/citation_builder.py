"""Deterministic citation text built from A's passage metadata (plan B3).

The decoder reasons; the final citation string comes from `canonical_body` and
`article` of a passage it actually received. Every candidate string is verified
before it is returned: citation_guard's own support rule must accept it against
its source passage, and the official extractor must only find bodies that the
evaluator would count as supported by that passage. Unverifiable -> not emitted.
"""
from __future__ import annotations

import re

from .guards import reference_support
from .legal import passage_bodies, references
from .official import official_bodies

CODE_NAMES = {
    "constitucion": "Constitución Política",
    "codigo_civil": "Código Civil",
    "codigo_penal": "Código Penal",
    "codigo_procedimiento_penal": "Código de Procedimiento Penal",
    "codigo_comercio": "Código de Comercio",
    "codigo_sustantivo_trabajo": "Código Sustantivo del Trabajo",
    "codigo_procesal_trabajo": "Código Procesal del Trabajo",
    "codigo_general_proceso": "Código General del Proceso",
    "cpaca": "Código de Procedimiento Administrativo y de lo Contencioso Administrativo",
    "estatuto_tributario": "Estatuto Tributario",
    "estatuto_consumidor": "Estatuto del Consumidor",
    "codigo_infancia": "Código de la Infancia y la Adolescencia",
    "codigo_nacional_policia": "Código Nacional de Seguridad y Convivencia Ciudadana",
    "codigo_disciplinario": "Código General Disciplinario",
}
KIND_NAMES = {"ley": "Ley", "decreto": "Decreto", "acto_legislativo": "Acto Legislativo",
              "resolucion": "Resolución", "circular": "Circular", "acuerdo": "Acuerdo", "decision": "Decisión Andina"}
_ARTICLE = re.compile(r"^\d+(?:[.\-]\d+)*[A-Za-z]?$")


def body_of(passage: dict) -> tuple | None:
    canonical = passage.get("canonical_body")
    if isinstance(canonical, (list, tuple)) and len(canonical) == 3:
        return tuple(None if v is None else str(v) for v in canonical)
    bodies = sorted(passage_bodies(passage), key=str)
    return bodies[0] if bodies else None


def _names(passage: dict) -> list[str]:
    body, names = body_of(passage), []
    if body:
        kind, number, year = body
        if kind in CODE_NAMES:
            names.append(CODE_NAMES[kind])
        elif kind == "jurisprudencia" and number and year:
            names.append(f"Sentencia {number} de {year}")
        elif kind in KIND_NAMES and number and year:
            names.append(f"{KIND_NAMES[kind]} {number} de {year}")
    norm_name = (passage.get("norm_name") or "").strip().rstrip(".")
    if norm_name and norm_name not in names:
        names.append(norm_name)
    return names


def _connector(name: str) -> str:
    return "del" if re.match(r"(?:Código|Estatuto|Decreto|Acto|Acuerdo)\b", name) else "de la"


def verified(candidate: str, passage: dict) -> bool:
    refs = references(candidate)
    if not refs or any(r.kind == "unresolved" or not r.complete for r in refs):
        return False
    if any(not reference_support(r, [passage]) for r in refs):
        return False
    cited = official_bodies(candidate)
    return bool(cited) and cited <= official_bodies(passage.get("text") or "")


def render_reference(passage: dict) -> str | None:
    """Most specific verifiable citation for one passage, or None."""
    names = _names(passage)
    article = str(passage.get("article") or "")
    body = body_of(passage)
    candidates = []
    if _ARTICLE.match(article) and not (body and body[0] == "jurisprudencia"):
        candidates += [f"artículo {article} {_connector(n)} {n}" for n in names]
    candidates += names
    return next((c for c in candidates if verified(c, passage)), None)


NEUTRAL_DISCARD = "No concuerda con la evidencia recuperada."


def attach_references(row: dict, evidence: list[dict], used_ids: list[str] | None = None, max_refs: int = 3) -> tuple[dict, list[str]]:
    """Write builder citations into the format's citation slot (mutates and returns row).

    semi_open: referencia_legal is replaced (the juez RAGAS never reads it).
    multiple_choice: appended to justificacion unless its bodies are already cited.
    open_ended: appended to marco_normativo (max 3, it is read by RAGAS) only if
    marco_normativo has no supported citation left after repair.
    """
    fmt = row.get("formato")
    refs = build_references(evidence, used_ids, 3 if fmt == "open_ended" else max_refs)
    if not refs:
        return row, refs
    if fmt == "semi_open":
        row["referencia_legal"] = "; ".join(refs)
    elif fmt == "multiple_choice":
        just = (row.get("justificacion") or "").strip()
        new = [r for r in refs if not official_bodies(r) <= official_bodies(just)]
        if new:
            row["justificacion"] = (just + " " if just else "") + "Fundamento normativo: " + "; ".join(new) + "."
        row["descarte_opciones"] = {k: (v if isinstance(v, str) and v.strip() else NEUTRAL_DISCARD)
                                    for k, v in (row.get("descarte_opciones") or {}).items()}
    elif fmt == "open_ended":
        marco = (row.get("marco_normativo") or "").strip()
        if not official_bodies(marco):
            row["marco_normativo"] = (marco + " " if marco else "") + "Normas aplicables: " + "; ".join(refs) + "."
    return row, refs


def build_references(passages: list[dict], used_ids: list[str] | None = None, max_refs: int = 3) -> list[str]:
    """Citations for the passages the decoder declared it used (else the first max_refs)."""
    by_id = {p["passage_id"]: p for p in passages[:10]}
    chosen = [by_id[i] for i in (used_ids or []) if i in by_id] or passages[:max_refs]
    refs: list[str] = []
    for passage in chosen:
        ref = render_reference(passage)
        if ref and ref not in refs:
            refs.append(ref)
        if len(refs) >= max_refs:
            break
    return refs
