import unittest
from types import SimpleNamespace

import numpy as np

from kingscode.generation.structured_json import response_schema
from kingscode.metadata import embedding_representation
from kingscode.neural import _LRUScoreCache, _reranker_pair_key
from kingscode.neural import DenseIndex
from kingscode.reasoning.contracts import Question
from kingscode.reasoning.pipeline import retrieval_views
from kingscode.reasoning.query import normalize_query
from kingscode.retrieval import BM25Index


class RetrievalDesignExperimentsTests(unittest.TestCase):
    def test_reranker_score_cache_is_bounded_lru_and_keys_full_pair_identity(self):
        cache = _LRUScoreCache(capacity=2)
        cache.put("a", 0.25)
        cache.put("b", 0.5)
        self.assertEqual(cache.get("a"), 0.25)  # a becomes most-recently used
        cache.put("c", 0.75)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("a"), 0.25)
        self.assertNotEqual(_reranker_pair_key("model", "q", "doc"),
                            _reranker_pair_key("model", "q2", "doc"))
        self.assertNotEqual(_reranker_pair_key("model", "q", "doc"),
                            _reranker_pair_key("model", "q", "doc2"))
        self.assertNotEqual(_reranker_pair_key("model", "q", "doc"),
                            _reranker_pair_key("model2", "q", "doc"))

    def test_context_representation_is_search_only_and_bm25_uses_it(self):
        passage = {"passage_id": "p1", "text": "Texto normativo literal", "norm_name": "Ley 100 de 1993",
                   "article": "14", "hierarchy_path": ["Ley 100 de 1993", "CAPÍTULO II"]}
        literal = passage["text"]
        search_text = embedding_representation(passage)
        index = BM25Index([passage], texts=[search_text])
        self.assertIn("Ley 100 de 1993", search_text)
        self.assertEqual(index.ranking("Ley 100 de 1993 artículo 14", 1)[0], [0])
        self.assertEqual(passage["text"], literal)

    def test_plan_roles_select_only_requested_frozen_view_and_keep_q0(self):
        question = Question(7, "¿Cuál es la regla?", "semi_open")
        plan = SimpleNamespace(views=("hechos", "elementos jurídicos", "vocabulario"),
                               view_roles=("Q1", "Q2", "Q3"))
        views = retrieval_views(question, normalize_query(question.text), "plan", plan, ("Q2",))
        self.assertEqual([v[2] for v in views], ["Q0", "Q2"])
        self.assertEqual(views[0][0], question.text)
        self.assertFalse(views[1][1])

    def test_option_support_is_auxiliary_cosine_by_passage_and_option(self):
        class Encoder:
            def encode(self, texts, **kwargs):
                return np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype="float32")
        dense = DenseIndex.__new__(DenseIndex)
        dense.encoder = Encoder()
        dense.query_instruction = "instruction"
        dense.passages = [{"passage_id": "p1"}, {"passage_id": "p2"}]
        dense.vectors = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype="float32")
        passages = [{"passage_id": "p2"}, {"passage_id": "p1"}]
        scores = dense.option_support("Q", {"A": "a", "B": "b"}, passages)
        self.assertGreater(scores["A"]["p1"], scores["A"]["p2"])
        self.assertGreater(scores["B"]["p2"], scores["B"]["p1"])

    def test_constrained_schema_enumerates_options_and_retrieved_ids(self):
        schema = response_schema("multiple_choice", {"A": "x", "B": "y"}, ["p1", "p2"], 5)
        properties = schema["properties"]
        self.assertEqual(properties["respuesta_correcta"]["enum"], ["A", "B"])
        self.assertEqual(properties["pasajes_usados"]["items"]["enum"], ["p1", "p2"])
        self.assertEqual(schema["additionalProperties"], False)


if __name__ == "__main__":
    unittest.main()
