"""B4: guarda de citas. Replica exactamente la logica del evaluador:
una cita (a nivel de cuerpo normativo: tipo+numero+ano, sin articulo) esta
respaldada si aparece en alguno de los primeros 10 pasajes entregados.

Cada cita sin respaldo resta el doble en el componente de citacion, asi que la
guarda elimina automaticamente (sin edicion manual) las oraciones que las
contienen. Todo queda registrado en el log de la corrida."""
from __future__ import annotations

import re

import citations

from .citerender import render_cite

MAX_EVID = 10
_SENT_SPLIT = re.compile(r"(?<=[.;:!?])\s+(?=[A-ZÁÉÍÓÚÑ0-9\"“(])")
_CITE_SPAN = re.compile(
    r"(?i)(?:\b(?:el|la|los|del|de la)\s+)?(?:\bart[ií]culos?\s+[\d\s,y]+(?:\s+(?:de|del)\s+(?:la|el)?\s*)?)?"
    r"\b(?:ley|decreto(?:\s+ley)?|resoluci[oó]n|circular|acuerdo|acto legislativo|sentencia)\s+"
    r"(?:n[°ºo]?\.?\s*)?[a-z]{0,3}-?\s*\d{1,5}\s*(?:de|del|/|-)\s*\d{2,4}")


def supported_bodies(passages: list[dict]) -> set[tuple]:
    s: set[tuple] = set()
    for p in passages[:MAX_EVID]:
        s |= citations.extract(str(p.get("texto") or ""))
    return citations.bodies(s)


def unsupported(text: str, supp: set[tuple]) -> set[tuple]:
    return citations.bodies(citations.extract(text or "")) - supp


def clean_text(text: str, supp: set[tuple]) -> tuple[str, int]:
    """Quita oraciones con citas sin respaldo. Si todo el campo quedaria vacio,
    conserva las oraciones borrando solo el fragmento de la cita."""
    if not text or not unsupported(text, supp):
        return text, 0
    sents = _SENT_SPLIT.split(text.strip())
    keep = [s for s in sents if not unsupported(s, supp)]
    removed = len(sents) - len(keep)
    if keep:
        return " ".join(keep), removed
    redacted = []
    for s in sents:
        s2 = _CITE_SPAN.sub("la norma aplicable", s)
        if unsupported(s2, supp):
            continue
        redacted.append(s2)
    return (" ".join(redacted) if redacted else ""), removed


def header_cites(p: dict) -> list[tuple]:
    """Citas del encabezado del pasaje (la norma de la que procede)."""
    head = (p.get("texto") or "")[:300]
    cs = citations.extract(head)
    return sorted(cs, key=lambda c: (c[3] is None, str(c)))


def build_refs(passages: list[dict], used_idx: list[int], max_cites: int) -> list[str]:
    """Referencias en texto, construidas por codigo a partir de los pasajes que
    el modelo declaro usar (o los primeros si no declaro ninguno)."""
    order = [i - 1 for i in used_idx if 1 <= i <= min(len(passages), MAX_EVID)]
    if not order:
        order = list(range(min(3, len(passages))))
    refs, seen_body = [], set()
    for i in order:
        for c in header_cites(passages[i]):
            b = c[:3]
            key = c if c[3] else b
            if key in seen_body:
                continue
            seen_body.add(key)
            refs.append(render_cite(c))
            break
        if len(refs) >= max_cites:
            break
    return refs


def citation_guard(row: dict, passages: list[dict]) -> dict:
    """Aplica la guarda a todos los campos de texto de una fila ya armada.
    Devuelve estadisticas; modifica row en sitio."""
    supp = supported_bodies(passages)
    fields = {"multiple_choice": ["justificacion"],
              "semi_open": ["respuesta", "referencia_legal"],
              "open_ended": ["marco_normativo", "analisis", "jurisprudencia", "conclusion"]}[row["formato"]]
    stats = {"oraciones_removidas": 0, "sin_respaldo_antes": 0}
    for f in fields:
        stats["sin_respaldo_antes"] += len(unsupported(row.get(f, ""), supp))
        before = row.get(f, "")
        row[f], n = clean_text(before, supp)
        stats["oraciones_removidas"] += n
        if f == "jurisprudencia" and n and not citations.extract(row[f]):
            row[f] = "No se identificó jurisprudencia específica en la evidencia recuperada."
    if row["formato"] == "multiple_choice":
        for k, v in list((row.get("descarte_opciones") or {}).items()):
            row["descarte_opciones"][k], _ = clean_text(v, supp)
    stats["sin_respaldo_despues"] = sum(len(unsupported(row.get(f, ""), supp)) for f in fields)
    return stats
