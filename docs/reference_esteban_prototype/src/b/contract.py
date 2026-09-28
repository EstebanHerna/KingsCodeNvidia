"""Contrato A -> B.

A entrega una funcion:
    retrieve(question: str, k: int, graph_mode: str = "auto") -> list[dict]

Cada pasaje es un dict con, como minimo:
    doc_id  str   id del documento, igual al de corpus_manifest.json
    texto   str   texto literal. DEBE empezar con el nombre completo de la norma,
                  p. ej. "Codigo Sustantivo del Trabajo. ARTICULO 60. ..." o
                  "Ley 1010 de 2006. ARTICULO 1. ...". Sin eso el evaluador no
                  liga la cita con la evidencia.
    inicio  int   offset de caracter en el documento (opcional pero recomendado)
    fin     int
    score   float
Campos opcionales que B aprovecha si existen: articulo, norma, via ("bm25",
"dense", "graph", "lookup"), vigente (bool).

B nunca lee BM25/FAISS/grafo por dentro: solo este contrato.
"""
from __future__ import annotations

import importlib
from typing import Callable

import citations  # modulo oficial

from .citerender import render_body

Retriever = Callable[..., list]


def load_retriever(spec: str) -> Retriever:
    if spec == "mock":
        return mock_retrieve
    mod, fn = spec.split(":")
    return getattr(importlib.import_module(mod), fn)


def mock_retrieve(question: str, k: int = 8, graph_mode: str = "auto") -> list[dict]:
    """Solo para probar el harness sin corpus. Crea pasajes con el encabezado de
    las normas que la propia pregunta menciona. NO sirve para la entrega."""
    bodies = sorted(citations.bodies(citations.extract(question)), key=str)
    out = []
    for i, b in enumerate(bodies[:k]):
        name = render_body(b)
        out.append({"doc_id": "mock_" + "_".join(str(x) for x in b if x),
                    "texto": f"{name}. PASAJE DE PRUEBA (mock, sin texto real).",
                    "inicio": 0, "fin": 60, "score": round(0.9 - 0.05 * i, 4), "via": "mock"})
    if not out:
        out.append({"doc_id": "mock_vacio", "texto": "PASAJE DE PRUEBA sin norma identificada.",
                    "inicio": 0, "fin": 40, "score": 0.1, "via": "mock"})
    return out


def check_passage(p: dict) -> list[str]:
    errs = []
    for f in ("doc_id", "texto"):
        if not p.get(f):
            errs.append(f"pasaje sin {f}")
    if p.get("texto") and not citations.extract(p["texto"][:250]):
        errs.append(f"{p.get('doc_id')}: el encabezado no contiene una norma reconocible por citations.py")
    return errs
