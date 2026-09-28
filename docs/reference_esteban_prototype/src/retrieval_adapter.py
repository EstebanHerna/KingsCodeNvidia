"""PLANTILLA PARA A. Este es el unico punto de union entre A y B.

A reemplaza el cuerpo de retrieve() por su recuperador real (BM25 + denso + RRF
+ reranker + grafo). B lo carga con  "retriever": "retrieval_adapter:retrieve".

Requisitos del contrato (ver b/contract.py):
  - determinista (mismo input -> mismo output) con el indice congelado
  - cada pasaje: doc_id, texto (empieza con el nombre de la norma), inicio, fin, score
  - graph_mode: "off" = solo ruta rapida; "on" = con expansion de grafo
"""
from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def _load():
    # Ejemplo: cargar indices una sola vez
    # import faiss, json, bm25s
    # index = faiss.read_index("indice/index.faiss")
    # chunks = [json.loads(l) for l in open("indice/chunks.jsonl", encoding="utf-8")]
    raise NotImplementedError("A: conectar aqui el recuperador real")


def retrieve(question: str, k: int = 10, graph_mode: str = "auto") -> list[dict]:
    _load()
    return []
