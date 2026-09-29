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

    def test_non_textual_query_views_are_rejected(self):
        with self.assertRaises(TypeError):
            normalize_query_views("question", ["ok", {"legal_basis":"secret"}])


if __name__=="__main__":
    unittest.main()
