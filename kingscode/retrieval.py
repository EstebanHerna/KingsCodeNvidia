"""Deterministic sparse/hybrid retrieval and bounded legal-graph expansion.

Public contract: retrieve(question, k, graph_mode='auto') -> list[passage].
Dense and reranking are explicit opt-ins: unavailable models fail, never silently
fall back. The module never opens sample_50 or expected answers.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
import math
from pathlib import Path
import re
from time import perf_counter
from typing import Sequence

from .common import ROOT, file_hash, indexable, normalize, read_json, read_jsonl, write_json
from .metadata import embedding_representation

STOP = set("a al algo ante bajo con contra cual cuando de del desde donde el ella ellas ellos en entre era es esa ese eso esta este esto estos estas fue ha han hasta hay la las le les lo los mas me mi muy ni no nos o para pero por que quien se ser si sin sobre son su sus un una unas uno unos y ya e u".split())
TOKENIZER_VERSION = "accent-fold-unicode-words-1"


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+|\d+[a-z]?", normalize(text)) if w not in STOP]


class BM25Index:
    def __init__(self, passages: list[dict], k1: float = 1.2, b: float = 0.75,
                 texts: list[str] | None = None):
        self.passages = passages
        self.texts = texts if texts is not None else [p["text"] for p in passages]
        if len(self.texts) != len(passages) or any(not isinstance(t, str) for t in self.texts):
            raise ValueError("BM25 text view must have one plain-text entry per passage")
        self.k1, self.b = k1, b
        self.lengths = []
        self.postings = defaultdict(list)
        for i, passage in enumerate(passages):
            tokens = tokenize(self.texts[i])
            self.lengths.append(len(tokens))
            for term, count in sorted(Counter(tokens).items()):
                self.postings[term].append([i, count])
        self.avgdl = sum(self.lengths) / max(1, len(self.lengths))

    def scores(self, question: str) -> dict[int, float]:
        result = defaultdict(float)
        n = len(self.passages)
        for token in sorted(set(tokenize(question))):
            hits = self.postings.get(token, [])
            if not hits:
                continue
            idf = math.log(1 + (n - len(hits) + 0.5) / (len(hits) + 0.5))
            for i, tf in hits:
                norm = self.k1 * (1 - self.b + self.b * self.lengths[i] / (self.avgdl or 1))
                result[i] += idf * tf * (self.k1 + 1) / (tf + norm)
        return dict(result)

    def ranking(self, question: str, k: int) -> tuple[list[int], dict[int, float]]:
        scores = self.scores(question)
        order = sorted(scores, key=lambda i: (-scores[i], self.passages[i]["passage_id"]))[:k]
        return order, scores

    def save(self, path: Path, corpus_sha256: str):
        write_json(path, {"tokenizer_version": TOKENIZER_VERSION, "corpus_sha256": corpus_sha256,
                          "k1": self.k1, "b": self.b, "avgdl": self.avgdl, "lengths": self.lengths,
                          "passage_ids": [p["passage_id"] for p in self.passages],
                          "postings": dict(sorted(self.postings.items()))})

    @classmethod
    def load(cls, path: Path, passages: list[dict], corpus_sha256: str):
        state = read_json(path)
        if state["corpus_sha256"] != corpus_sha256 or state["tokenizer_version"] != TOKENIZER_VERSION:
            raise ValueError("Stale BM25 index; rebuild corpus")
        if state["passage_ids"] != [p["passage_id"] for p in passages]:
            raise ValueError("BM25 passage ordering mismatch")
        obj = cls.__new__(cls)
        obj.passages = passages
        obj.texts = [p["text"] for p in passages]
        for name in ["k1", "b", "avgdl", "lengths", "postings"]:
            setattr(obj, name, state[name])
        return obj


def reciprocal_rank_fusion(rankings: list[list[int]], constant: int = 60) -> dict[int, float]:
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, i in enumerate(dict.fromkeys(ranking), 1):
            scores[i] += 1 / (constant + rank)
    return dict(scores)


def normalize_query_views(question: str, query_views: Sequence[str] | None = None) -> list[str]:
    """Keep the user's question first; deduplicate textual views deterministically."""
    if not isinstance(question, str):
        raise TypeError("question must be plain text")
    if query_views is None:
        supplied = []
    elif isinstance(query_views, (list, tuple)):
        supplied = list(query_views)
    else:
        raise TypeError("query_views must be a list or tuple of plain text")
    views = []
    seen = set()
    for view in [question, *supplied]:
        if not isinstance(view, str):
            raise TypeError("every query view must be plain text")
        key = normalize(view).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        views.append(view.strip())
    return views


def default_graph_route(question: str) -> bool:
    """Provisional deterministic fallback, replaceable by member B's router."""
    return bool(re.search(r"\b(remisi[oó]n|remite|remiten|modific\w*|derog\w*|reglament\w*|concordancia|par[aá]grafo|inciso)\b", question, re.I))


class Retriever:
    def __init__(self, corpus_dir: str | Path | None = None, *, mode: str = "bm25", rerank: bool = False,
                 graph_router=None, candidate_k: int = 30, graph_budget: int = 10, exact_locator: bool = False,
                 reranker_batch_size: int = 2, retrieval_text_mode: str = "literal",
                 dense_index_dir: str | Path | None = None, embedding_instruction: str | None = None,
                 reranker_instruction: str | None = None):
        if mode not in {"bm25", "dense", "hybrid"}:
            raise ValueError("mode must be bm25, dense or hybrid")
        if candidate_k < 1 or graph_budget < 0 or reranker_batch_size < 1:
            raise ValueError("candidate_k and reranker_batch_size must be positive; graph_budget nonnegative")
        self.directory = Path(corpus_dir) if corpus_dir else ROOT / "corpus"
        self.corpus_hash = file_hash(self.directory / "passages.jsonl")
        self.passages = [p for p in read_jsonl(self.directory / "passages.jsonl") if indexable(p)]
        passage_ids = [p.get("passage_id") for p in self.passages]
        if any(not isinstance(passage_id, str) or not passage_id for passage_id in passage_ids):
            raise ValueError("Every indexed passage must have a nonempty string passage_id")
        if len(passage_ids) != len(set(passage_ids)):
            raise ValueError("Duplicate passage_id values make RRF identity ambiguous")
        if retrieval_text_mode not in {"literal", "context"}:
            raise ValueError("retrieval_text_mode must be literal or context")
        self.retrieval_text_mode = retrieval_text_mode
        self.search_texts = ([p["text"] for p in self.passages] if retrieval_text_mode == "literal"
                             else [embedding_representation(p) for p in self.passages])
        if retrieval_text_mode == "literal":
            self.bm25 = BM25Index.load(self.directory / "index/bm25.json", self.passages, self.corpus_hash)
        else:
            # Search-only metadata view: neither frozen passages nor evidence text changes.
            self.bm25 = BM25Index(self.passages, texts=self.search_texts)
        self.mode, self.candidate_k, self.graph_budget = mode, candidate_k, graph_budget
        from .legal_locator import LegalLocator
        self.legal_locator = LegalLocator(self.passages) if exact_locator else None
        self.router = graph_router or default_graph_route
        self.node_passages = defaultdict(set)
        for i, p in enumerate(self.passages):
            for nid in p["graph_node_ids"]:
                self.node_passages[nid].add(i)
        self.adjacency = defaultdict(list)
        for e in read_jsonl(self.directory / "graph/edges.jsonl"):
            self.adjacency[e["source"]].append((e["target"], e))
            # Relational traversal is bidirectional, edge direction is preserved
            # in evidence metadata. Never expand up to an entire parent norm.
            if e["relation"] != "CONTIENE":
                self.adjacency[e["target"]].append((e["source"], e))
        self.dense = self.reranker = None
        if mode in {"dense", "hybrid"}:
            from .neural import DenseIndex
            if retrieval_text_mode == "context" and dense_index_dir is None:
                raise ValueError("context dense retrieval needs a separately built --dense-index-dir")
            self.dense = DenseIndex(self.directory, self.passages, self.corpus_hash,
                                    index_dir=dense_index_dir, query_instruction=embedding_instruction,
                                    representation_id=("context_metadata_v1" if retrieval_text_mode == "context"
                                                      else "source_text_v1"))
        if rerank:
            from .neural import QwenReranker
            self.reranker = QwenReranker(batch_size=reranker_batch_size, instruction=reranker_instruction)

    def retrieve(self, question: str, k: int = 8, graph_mode: str = "auto",
                 query_views: Sequence[str] | None = None) -> list[dict]:
        started = perf_counter()
        if not isinstance(question, str):
            raise TypeError("question must be plain text, never a sample/answer record")
        views = normalize_query_views(question, query_views)
        if graph_mode not in {"off", "auto", "on"}:
            raise ValueError("graph_mode must be off, auto or on")
        if not isinstance(k, int) or isinstance(k, bool) or k < 0:
            raise ValueError("k must be a nonnegative integer")
        if not views or k == 0:
            return []
        count = max(k, self.candidate_k)
        sparse_rankings, dense_rankings = [], []
        bm_scores, dense_scores = {}, {}
        bm25_ms = dense_ms = fusion_ms = locator_ms = graph_ms = reranker_ms = 0.0
        dense_query_profile = {"encoded_queries": 0, "encode_batches": 0}
        for view_index, view in enumerate(views):
            stage = perf_counter()
            sparse, view_bm_scores = self.bm25.ranking(view, count)
            bm25_ms += (perf_counter() - stage) * 1000
            sparse_rankings.append(sparse)
            if view_index == 0:
                bm_scores = view_bm_scores
        if self.dense is not None:
            stage = perf_counter()
            dense_results = self.dense.ranking_many(views, count)
            dense_ms += (perf_counter() - stage) * 1000
            dense_rankings = [ranking for ranking, _ in dense_results]
            if dense_results:
                dense_scores = dense_results[0][1]
            dense_query_profile = dict(getattr(self.dense, "last_query_profile", dense_query_profile))
        stage = perf_counter()
        if self.mode == "bm25":
            ranks = sparse_rankings
            fused = reciprocal_rank_fusion(ranks)
            scores = fused if len(views) > 1 else dict(bm_scores)
        elif self.mode == "dense":
            ranks = dense_rankings
            fused = reciprocal_rank_fusion(ranks)
            scores = fused if len(views) > 1 else dict(dense_scores)
        else:
            ranks = [ranking for pair in zip(sparse_rankings, dense_rankings) for ranking in pair]
            fused = reciprocal_rank_fusion(ranks)
            scores = fused.copy()
        candidates = set(i for ranking in ranks for i in ranking)
        base = sorted(candidates, key=lambda i: (-scores.get(i, 0), self.passages[i]["passage_id"]))[:count]
        candidates = set(base)
        fusion_ms += (perf_counter() - stage) * 1000
        locator_result = None
        if getattr(self, "legal_locator", None) is not None:
            stage = perf_counter()
            from .legal_locator import candidate_union
            locator_result = self.legal_locator.resolve(question)
            candidates = set(candidate_union(base, locator_result["indices"]))
            locator_ms += (perf_counter() - stage) * 1000
        graph_scores, graph_evidence = {}, defaultdict(list)
        active = graph_mode == "on" or graph_mode == "auto" and bool(self.router(question))
        if active and base and self.graph_budget:
            stage = perf_counter()
            graph_dense_ms = 0.0
            for seed_rank, i in enumerate(base[:5], 1):
                # Skip the norm root: a query about one article must not fan out
                # through every article or every citation in the whole statute.
                for nid in self.passages[i]["graph_node_ids"][1:]:
                    for target, edge in self.adjacency.get(nid, []):
                        neighbors = sorted(self.node_passages.get(target, []),
                                           key=lambda j: (-bm_scores.get(j, 0), self.passages[j]["passage_id"]))[:2]
                        for j in neighbors:
                            if j == i or bm_scores.get(j, 0) <= 0:
                                continue
                            graph_scores[j] = max(graph_scores.get(j, 0), 1 / (60 + seed_rank))
                            graph_evidence[j].append(edge)
            expansion = sorted(graph_scores, key=lambda i: (-graph_scores[i], -bm_scores.get(i, 0), self.passages[i]["passage_id"]))[:self.graph_budget]
            candidates.update(expansion)
            if self.mode == "bm25":
                # Bounded, declared structural prior; evaluated OFF vs AUTO.
                scale = max((bm_scores.get(i, 0) for i in base), default=0) * 0.15 * 61
                for i in expansion:
                    scores[i] = bm_scores.get(i, 0) + scale * graph_scores[i]
            elif self.mode == "hybrid":
                for i in expansion:
                    scores[i] = scores.get(i, 0) + 0.25 * graph_scores[i]
            else:
                # Dense scores must be computed for added candidates too.
                dense_stage = perf_counter()
                extra = self.dense.score_indices(question, expansion)
                graph_dense_ms = (perf_counter() - dense_stage) * 1000
                dense_ms += graph_dense_ms
                dense_scores.update(extra)
                for i in expansion:
                    scores[i] = extra[i] + 0.05 * graph_scores[i] * 61
            graph_ms += max(0.0, (perf_counter() - stage) * 1000 - graph_dense_ms)
        if self.dense:
            stage = perf_counter()
            dense_scores.update(self.dense.score_indices(question, candidates))
            dense_ms += (perf_counter() - stage) * 1000
        order = sorted(candidates, key=lambda i: (-scores.get(i, 0), self.passages[i]["passage_id"]))
        candidate_count = len(order)
        rerank_scores = {}
        if self.reranker and order:
            stage = perf_counter()
            values = self.reranker.score(question, [self.search_texts[i] for i in order])
            reranker_ms = (perf_counter() - stage) * 1000
            rerank_scores = dict(zip(order, values))
            order.sort(key=lambda i: (-rerank_scores[i], self.passages[i]["passage_id"]))
        reranker_batch_size = getattr(self.reranker, "batch_size", None) if self.reranker else None
        reranker_pairs = candidate_count if self.reranker else 0
        profile = {
            "mode": self.mode,
            "retrieval_text_mode": self.retrieval_text_mode,
            "candidate_k": self.candidate_k,
            "graph_budget": self.graph_budget,
            "query_view_count": len(views),
            "dense_encoded_queries": dense_query_profile["encoded_queries"],
            "dense_encode_batches": dense_query_profile["encode_batches"],
            "candidate_count": candidate_count,
            "reranker_pairs": reranker_pairs,
            "reranker_batch_size": reranker_batch_size,
            "reranker_batches": ((reranker_pairs + reranker_batch_size - 1) // reranker_batch_size
                                 if reranker_pairs and isinstance(reranker_batch_size, int) and reranker_batch_size > 0
                                 else None),
            "bm25_ms": round(bm25_ms, 3),
            "dense_ms": round(dense_ms, 3),
            "fusion_ms": round(fusion_ms, 3),
            "locator_ms": round(locator_ms, 3),
            "graph_ms": round(graph_ms, 3),
            "reranker_ms": round(reranker_ms, 3),
            "total_ms": round((perf_counter() - started) * 1000, 3),
        }
        output = []
        for rank, i in enumerate(order[:k], 1):
            p = deepcopy(self.passages[i])
            p["scores"] = {"bm25": bm_scores.get(i), "dense": dense_scores.get(i),
                           "rrf": fused.get(i), "graph": graph_scores.get(i), "reranker": rerank_scores.get(i)}
            p["score"] = rerank_scores.get(i, scores.get(i, 0))
            p["retrieval"] = {"rank": rank, "mode": self.mode, "graph_mode": graph_mode,
                              "retrieval_text_mode": self.retrieval_text_mode,
                              "graph_active": active, "corpus_sha256": self.corpus_hash,
                              "query_view_count": len(views),
                              "profile": profile,
                              "graph_evidence": graph_evidence.get(i, [])}
            if locator_result is not None:
                p["locator"] = {"version": locator_result["version"], "hit": i in locator_result["hits"],
                                "matches": locator_result["hits"].get(i, []),
                                "unresolved": locator_result["unresolved"]}
                p["retrieval"]["candidate_sources"] = (["general"] if i in base else []) + (
                    ["exact_locator"] if i in locator_result["hits"] else []) + (["graph"] if i in graph_evidence else [])
                p["retrieval"]["general_candidate_count"] = len(base)
                p["retrieval"]["locator_candidate_count"] = len(locator_result["indices"])
                p["retrieval"]["union_candidate_count"] = len(candidates)
            output.append(p)
        return output


@lru_cache(maxsize=2)
def _default_retriever(corpus_hash: str):
    # CPU-compatible public profile. Neural execution remains explicit. Class
    # defaults preserve historical R0-R8; no graph/diversity enabled by default.
    return Retriever(exact_locator=True, graph_router=lambda _question: False)


def retrieve(question: str, k: int = 8, graph_mode: str = "auto",
             query_views: Sequence[str] | None = None) -> list[dict]:
    return _default_retriever(file_hash(ROOT / "corpus/passages.jsonl")).retrieve(
        question, k, graph_mode, query_views=query_views)
