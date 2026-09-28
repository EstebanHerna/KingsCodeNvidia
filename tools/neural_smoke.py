"""Real-weight CPU/GPU smoke on existing official passages, never synthetic data."""
from pathlib import Path
import sys
import time
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from kingscode.common import ROOT, read_json, read_jsonl, file_hash, indexable, write_json, write_jsonl
from kingscode.neural import QwenEncoder, QwenReranker, configuration
from kingscode.retrieval import BM25Index, Retriever


def main():
    passages = read_jsonl(ROOT / "corpus/passages.jsonl")
    selected = [next(p for p in passages if p["doc_id"] == doc and p["article"] == article and indexable(p))
                for doc, article in [("constitucion", "1"), ("codigo_general_proceso", "1")]]
    texts = [p["text"] for p in selected]
    # Use a literal source heading as the smoke query; no generated QA dataset.
    query = selected[0]["norm_name"]
    start = time.perf_counter()
    encoder = QwenEncoder()
    embeddings = encoder.encode(texts)
    a, b = encoder.encode([query], query=True), encoder.encode([query], query=True)
    if not np.allclose(np.linalg.norm(embeddings, axis=1), 1, atol=1e-5) or not np.array_equal(a, b):
        raise RuntimeError("Encoder normalization/determinism failed")
    encoder_seconds = time.perf_counter() - start
    # Exercise the actual saved-vector loader and public retrieval paths on a
    # clearly separate two-source smoke index, never the competitive corpus.
    smoke_dir = ROOT / "tmp/neural_smoke"
    write_jsonl(smoke_dir / "passages.jsonl", selected)
    write_jsonl(smoke_dir / "graph/edges.jsonl", [])
    corpus_hash = file_hash(smoke_dir / "passages.jsonl")
    BM25Index(selected).save(smoke_dir / "index/bm25.json", corpus_hash)
    np.save(smoke_dir / "index/dense.npy", embeddings, allow_pickle=False)
    write_json(smoke_dir / "index/dense.meta.json", {
        "corpus_sha256": corpus_hash, "passage_ids": [p["passage_id"] for p in selected],
        "dimension": embeddings.shape[1], "vectors_sha256": file_hash(smoke_dir / "index/dense.npy"),
        "config": configuration(), "model_lock": read_json(ROOT / "config/models.lock.json")[configuration()["embedding_model"]]})
    integration = {}
    with patch("kingscode.neural.QwenEncoder", return_value=encoder):
        for mode in ["dense", "hybrid"]:
            retriever = Retriever(smoke_dir, mode=mode)
            result = retriever.retrieve(query, 2, "off")
            if result != retriever.retrieve(query, 2, "off") or result[0]["doc_id"] != selected[0]["doc_id"]:
                raise RuntimeError(f"{mode} retrieval smoke failed")
            integration[mode] = {"passage_ids": [p["passage_id"] for p in result], "scores": [p["scores"] for p in result]}
    # The query is cached in this two-source hybrid index; release the encoder
    # before loading the reranker to keep the CPU smoke's memory small.
    retriever.dense.encoder = None
    del encoder
    import gc
    gc.collect()
    start = time.perf_counter()
    reranker = QwenReranker()
    first = reranker.score(query, texts)
    second = reranker.score(query, texts)
    if first != second or not all(0 <= x <= 1 for x in first):
        raise RuntimeError("Reranker scoring/determinism failed")
    retriever.reranker = reranker
    result = retriever.retrieve(query, 2, "off")
    if result[0]["doc_id"] != selected[0]["doc_id"] or any(p["scores"]["reranker"] is None for p in result):
        raise RuntimeError("Hybrid reranker integration failed")
    integration["hybrid_reranker"] = {"passage_ids": [p["passage_id"] for p in result], "scores": [p["scores"] for p in result]}
    result = {"ok": True, "config": configuration(),
              "corpus_sha256": file_hash(ROOT / "corpus/passages.jsonl"),
              "model_lock": read_json(ROOT / "config/models.lock.json"),
              "integration": integration,
              "embedding_shape": list(embeddings.shape),
              "embedding_cosines": (embeddings @ a[0]).tolist(), "reranker_probabilities": first,
              "encoder_seconds": encoder_seconds, "reranker_seconds": time.perf_counter() - start,
              "passage_ids": [p["passage_id"] for p in selected], "scope": "real weights, two official passages; not full-corpus benchmark"}
    write_json(ROOT / "reports/neural_smoke.json", result)
    print(result)


if __name__ == "__main__":
    main()
