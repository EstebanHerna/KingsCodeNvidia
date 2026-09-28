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

from .common import ROOT, file_hash, indexable, normalize, read_json, read_jsonl, write_json

STOP = set("a al algo ante bajo con contra cual cuando de del desde donde el ella ellas ellos en entre era es esa ese eso esta este esto estos estas fue ha han hasta hay la las le les lo los mas me mi muy ni no nos o para pero por que quien se ser si sin sobre son su sus un una unas uno unos y ya e u".split())
TOKENIZER_VERSION = "accent-fold-unicode-words-1"


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+|\d+[a-z]?", normalize(text)) if w not in STOP]


class BM25Index:
    def __init__(self, passages: list[dict], k1: float = 1.2, b: float = 0.75):
        self.passages = passages
        self.k1, self.b = k1, b
        self.lengths = []
        self.postings = defaultdict(list)
        for i, passage in enumerate(passages):
            tokens = tokenize(passage["text"])
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
        for name in ["k1", "b", "avgdl", "lengths", "postings"]:
            setattr(obj, name, state[name])
        return obj


def reciprocal_rank_fusion(rankings: list[list[int]], constant: int = 60) -> dict[int, float]:
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, i in enumerate(dict.fromkeys(ranking), 1):
            scores[i] += 1 / (constant + rank)
    return dict(scores)


def default_graph_route(question: str) -> bool:
    """Provisional deterministic fallback, replaceable by member B's router."""
    return bool(re.search(r"\b(remisi[oó]n|remite|remiten|modific\w*|derog\w*|reglament\w*|concordancia|par[aá]grafo|inciso)\b", question, re.I))


class Retriever:
    def __init__(self, corpus_dir: str | Path | None = None, *, mode: str = "bm25", rerank: bool = False,
                 graph_router=None, candidate_k: int = 30, graph_budget: int = 10):
        if mode not in {"bm25", "dense", "hybrid"}:
            raise ValueError("mode must be bm25, dense or hybrid")
        if candidate_k < 1 or graph_budget < 0:
            raise ValueError("candidate_k must be positive and graph_budget nonnegative")
        self.directory = Path(corpus_dir) if corpus_dir else ROOT / "corpus"
        self.corpus_hash = file_hash(self.directory / "passages.jsonl")
        self.passages = [p for p in read_jsonl(self.directory / "passages.jsonl") if indexable(p)]
        self.bm25 = BM25Index.load(self.directory / "index/bm25.json", self.passages, self.corpus_hash)
        self.mode, self.candidate_k, self.graph_budget = mode, candidate_k, graph_budget
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
            self.dense = DenseIndex(self.directory, self.passages, self.corpus_hash)
        if rerank:
            from .neural import QwenReranker
            self.reranker = QwenReranker()

    def retrieve(self, question: str, k: int = 8, graph_mode: str = "auto") -> list[dict]:
        if not isinstance(question, str):
            raise TypeError("question must be plain text, never a sample/answer record")
        if graph_mode not in {"off", "auto", "on"}:
            raise ValueError("graph_mode must be off, auto or on")
        if not isinstance(k, int) or isinstance(k, bool) or k < 0:
            raise ValueError("k must be a nonnegative integer")
        if not question.strip() or k == 0:
            return []
        count = max(k, self.candidate_k)
        sparse, bm_scores = self.bm25.ranking(question, count)
        dense, dense_scores = ([], {}) if self.dense is None else self.dense.ranking(question, count)
        ranks = [sparse] if self.mode == "bm25" else [dense] if self.mode == "dense" else [sparse, dense]
        fused = reciprocal_rank_fusion(ranks)
        scores = dict(bm_scores) if self.mode == "bm25" else dict(dense_scores) if self.mode == "dense" else fused.copy()
        candidates = set(i for ranking in ranks for i in ranking)
        base = sorted(candidates, key=lambda i: (-scores.get(i, 0), self.passages[i]["passage_id"]))[:count]
        candidates = set(base)
        graph_scores, graph_evidence = {}, defaultdict(list)
        active = graph_mode == "on" or graph_mode == "auto" and bool(self.router(question))
        if active and base and self.graph_budget:
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
                extra = self.dense.score_indices(question, expansion)
                dense_scores.update(extra)
                for i in expansion:
                    scores[i] = extra[i] + 0.05 * graph_scores[i] * 61
        if self.dense:
            dense_scores.update(self.dense.score_indices(question, candidates))
        order = sorted(candidates, key=lambda i: (-scores.get(i, 0), self.passages[i]["passage_id"]))
        rerank_scores = {}
        if self.reranker and order:
            values = self.reranker.score(question, [self.passages[i]["text"] for i in order])
            rerank_scores = dict(zip(order, values))
            order.sort(key=lambda i: (-rerank_scores[i], self.passages[i]["passage_id"]))
        output = []
        for rank, i in enumerate(order[:k], 1):
            p = deepcopy(self.passages[i])
            p["scores"] = {"bm25": bm_scores.get(i), "dense": dense_scores.get(i),
                           "rrf": fused.get(i), "graph": graph_scores.get(i), "reranker": rerank_scores.get(i)}
            p["score"] = rerank_scores.get(i, scores.get(i, 0))
            p["retrieval"] = {"rank": rank, "mode": self.mode, "graph_mode": graph_mode,
                              "graph_active": active, "corpus_sha256": self.corpus_hash,
                              "graph_evidence": graph_evidence.get(i, [])}
            output.append(p)
        return output


@lru_cache(maxsize=2)
def _default_retriever(corpus_hash: str):
    return Retriever()


def retrieve(question: str, k: int = 8, graph_mode: str = "auto") -> list[dict]:
    return _default_retriever(file_hash(ROOT / "corpus/passages.jsonl")).retrieve(question, k, graph_mode)
