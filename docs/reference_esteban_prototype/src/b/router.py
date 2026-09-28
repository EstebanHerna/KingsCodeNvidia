"""B2: router determinista del grafo y fusion de consultas.

Regla: el grafo cuesta latencia y mete ruido. Solo se activa con senales
explicitas o cuando la ruta rapida recupera poco."""
from __future__ import annotations

from .query import NormalizedQuery


def route_graph(nq: NormalizedQuery, flat_passages: list[dict], mode: str = "auto",
                low_score: float = 0.35) -> str:
    if mode in ("off", "on"):
        return mode
    s = nq.signals
    if s["temporal"] or s["remision"] or s["jerarquia"]:
        return "on"
    if s["n_normas"] >= 2:
        return "on"
    if not flat_passages:
        return "on"
    top = max((p.get("score") or 0.0) for p in flat_passages)
    if top < low_score:
        return "on"
    return "off"


def rrf_merge(lists: list[list[dict]], k: int, c: int = 60) -> list[dict]:
    """Reciprocal Rank Fusion entre varias listas de pasajes (misma pregunta,
    distintas consultas). Clave de identidad: doc_id + inicio."""
    agg: dict[tuple, dict] = {}
    for lst in lists:
        for rank, p in enumerate(lst):
            key = (p.get("doc_id"), p.get("inicio"), p.get("texto", "")[:80])
            if key not in agg:
                agg[key] = {"p": p, "s": 0.0}
            agg[key]["s"] += 1.0 / (c + rank + 1)
    ranked = sorted(agg.values(), key=lambda x: (-x["s"], str(x["p"].get("doc_id")), x["p"].get("inicio") or 0))
    return [x["p"] for x in ranked[:k]]


def lookup_first(passages: list[dict], nq: NormalizedQuery) -> list[dict]:
    """Sube al frente los pasajes cuyo encabezado coincide con una norma que la
    pregunta menciona explicitamente (busqueda exacta > similitud)."""
    import citations
    wanted = set(nq.bodies)
    if not wanted:
        return passages
    hit, rest = [], []
    for p in passages:
        b = citations.bodies(citations.extract(p.get("texto", "")[:300]))
        (hit if b & wanted else rest).append(p)
    return hit + rest
