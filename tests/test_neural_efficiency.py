import unittest
from collections import OrderedDict

import numpy as np

from kingscode.neural import DenseIndex, QUERY_SCORE_CACHE_SIZE, _prepare_reranker_input_ids


class NeuralEfficiencyTests(unittest.TestCase):
    def test_dense_query_scores_are_cached_for_repeated_graph_pass(self):
        class Encoder:
            calls = 0
            def encode(self, questions, *, query=False):
                self.calls += 1
                self.assert_query = query
                return np.asarray([[1.0, 0.0]], dtype="float32")

        dense = DenseIndex.__new__(DenseIndex)
        dense.vectors = np.asarray([[1.0, 2.0], [3.0, 4.0]], dtype="float32")
        dense.encoder = Encoder()
        dense._score_cache = OrderedDict()
        self.assertEqual(dense.all_scores("q").tolist(), [1.0, 3.0])
        self.assertEqual(dense.score_indices("q", [1]), {1: 3.0})
        self.assertEqual(dense.encoder.calls, 1)
        self.assertTrue(dense.encoder.assert_query)

    def test_dense_query_views_are_encoded_in_one_bounded_batch_sequence(self):
        class Encoder:
            config = {"batch_size": 2}
            calls = []
            def encode(self, questions, *, query=False):
                self.calls.append((list(questions), query))
                vectors = {"alpha": [1.0, 0.0], "beta": [0.0, 1.0]}
                return np.asarray([vectors[q] for q in questions], dtype="float32")

        dense = DenseIndex.__new__(DenseIndex)
        dense.vectors = np.asarray([[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]], dtype="float32")
        dense.encoder = Encoder()
        dense.passages = [{"passage_id": f"p{i}"} for i in range(3)]
        dense._score_cache = OrderedDict()
        ranked = dense.ranking_many(["alpha", "beta"], 1)
        self.assertEqual([row[0][0] for row in ranked], [0, 1])
        self.assertEqual(dense.encoder.calls, [(["alpha", "beta"], True)])
        self.assertEqual(dense.last_query_profile, {"encoded_queries": 2, "encode_batches": 1})

    def test_dense_query_score_cache_is_bounded(self):
        class Encoder:
            def encode(self, questions, *, query=False):
                return np.asarray([[1.0]], dtype="float32")

        dense = DenseIndex.__new__(DenseIndex)
        dense.vectors = np.asarray([[1.0]], dtype="float32")
        dense.encoder = Encoder()
        dense._score_cache = OrderedDict()
        for i in range(QUERY_SCORE_CACHE_SIZE + 3):
            dense.all_scores(f"q{i}")
        self.assertEqual(len(dense._score_cache), QUERY_SCORE_CACHE_SIZE)
        self.assertNotIn("q0", dense._score_cache)

    def test_reranker_preflights_all_pairs_before_model_work(self):
        class Tokenizer:
            calls = 0
            def __call__(self, texts, **kwargs):
                self.calls += 1
                return {"input_ids": [[1] * (10 if "LONG" in text else 2) for text in texts]}

        tokenizer = Tokenizer()
        config = {"instruction": "judge", "max_length": 8}
        with self.assertRaisesRegex(ValueError, "exceeds max_length"):
            _prepare_reranker_input_ids(tokenizer, "q", ["short", "LONG"], config, [0], [0])
        self.assertEqual(tokenizer.calls, 1)


if __name__ == "__main__":
    unittest.main()
