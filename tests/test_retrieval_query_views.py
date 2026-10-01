import unittest
from collections import defaultdict
from kingscode.retrieval import Retriever, normalize_query_views


class FakeBM25:
    def __init__(self):
        self.queries = []
    def ranking(self, query, count):
        self.queries.append(query)
        return ([0] if query == "consulta base" else [1]), ({0: 1.0} if query == "consulta base" else {1: 1.0})


class FakeLocator:
    def __init__(self):
        self.queries = []
    def resolve(self, query):
        self.queries.append(query)
        return {"version": "test", "indices": set(), "hits": {}, "unresolved": []}


class FakeReranker:
    config = {"batch_size": 2}
    def __init__(self):
        self.documents = []
    def score(self, question, documents):
        self.documents.extend(documents)
        return [float(i) for i, _ in enumerate(documents)]


class FakeDense:
    last_query_profile = {"encoded_queries": 2, "encode_batches": 1}
    def __init__(self):
        self.queries = []
    def ranking_many(self, queries, count):
        self.queries.append(list(queries))
        return [([1], {1: 0.9}), ([0], {0: 0.8})]
    def score_indices(self, question, indices):
        return {i: 0.5 for i in indices}


class QueryViewsTests(unittest.TestCase):
    def test_normalization_keeps_original_first_and_deduplicates(self):
        self.assertEqual(normalize_query_views("Consulta base", ["consulta BASE", "vista alterna", "  "]),
                         ["Consulta base", "vista alterna"])

    def test_generated_views_are_fused_but_locator_receives_only_original_question(self):
        r=Retriever.__new__(Retriever)
        r.mode="bm25"; r.candidate_k=2; r.graph_budget=0; r.corpus_hash="fixture"
        r.passages=[
            {"passage_id":"p0","text":"texto cero","graph_node_ids":["root","n0"]},
            {"passage_id":"p1","text":"texto uno","graph_node_ids":["root","n1"]}]
        r.bm25=FakeBM25(); r.dense=None; r.reranker=None; r.legal_locator=FakeLocator()
        r.router=lambda _q:False; r.adjacency=defaultdict(list); r.node_passages=defaultdict(set)
        rows=r.retrieve("consulta base",2,"off",query_views=["consulta alterna"])
        self.assertEqual(r.bm25.queries,["consulta base","consulta alterna"])
        self.assertEqual(r.legal_locator.queries,["consulta base"])
        self.assertEqual([x["passage_id"] for x in rows],["p0","p1"])
        self.assertTrue(all(x["retrieval"]["query_view_count"]==2 for x in rows))
        profile = rows[0]["retrieval"]["profile"]
        self.assertEqual((profile["candidate_count"], profile["reranker_pairs"]), (2, 0))
        self.assertEqual(profile["candidate_k"], 2)
        self.assertTrue(all(profile[name] >= 0 for name in ("bm25_ms", "dense_ms", "fusion_ms", "locator_ms", "graph_ms", "reranker_ms", "total_ms")))

    def test_profile_counts_reranker_pairs_and_batches(self):
        r=Retriever.__new__(Retriever)
        r.mode="bm25"; r.candidate_k=2; r.graph_budget=0; r.corpus_hash="fixture"
        r.passages=[
            {"passage_id":"p0","text":"texto cero","graph_node_ids":["root","n0"]},
            {"passage_id":"p1","text":"texto uno","graph_node_ids":["root","n1"]}]
        r.bm25=FakeBM25(); r.dense=None; r.reranker=FakeReranker(); r.legal_locator=None
        r.router=lambda _q:False; r.adjacency=defaultdict(list); r.node_passages=defaultdict(set)
        rows=r.retrieve("consulta base",2,"off")
        profile = rows[0]["retrieval"]["profile"]
        self.assertEqual((profile["reranker_pairs"], profile["reranker_batch_size"], profile["reranker_batches"]), (1, 2, 1))
        self.assertEqual(profile["candidate_count"], 1)

    def test_hybrid_retriever_batches_dense_query_views_and_reports_them(self):
        r=Retriever.__new__(Retriever)
        r.mode="hybrid"; r.candidate_k=2; r.graph_budget=0; r.corpus_hash="fixture"
        r.passages=[
            {"passage_id":"p0","text":"texto cero","graph_node_ids":["root","n0"]},
            {"passage_id":"p1","text":"texto uno","graph_node_ids":["root","n1"]}]
        r.bm25=FakeBM25(); r.dense=FakeDense(); r.reranker=None; r.legal_locator=None
        r.router=lambda _q:False; r.adjacency=defaultdict(list); r.node_passages=defaultdict(set)
        rows=r.retrieve("consulta base",2,"off",query_views=["consulta alterna"])
        self.assertEqual(r.dense.queries, [["consulta base", "consulta alterna"]])
        profile = rows[0]["retrieval"]["profile"]
        self.assertEqual((profile["dense_encoded_queries"], profile["dense_encode_batches"]), (2, 1))

    def test_non_textual_query_views_are_rejected(self):
        with self.assertRaises(TypeError):
            normalize_query_views("question", ["ok", {"legal_basis":"secret"}])


if __name__=="__main__":
    unittest.main()
