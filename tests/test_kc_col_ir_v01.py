import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import verify_kc_col_ir_v01
from tools import independent_ir_v2


class IndependentBenchmarkTests(unittest.TestCase):
    def test_inventory_and_deterministic_sample_are_valid(self):
        result = verify_kc_col_ir_v01.verify()
        self.assertEqual(result["jep_pool"], 62)
        self.assertEqual(result["primary_dev_annotation_batch"], 30)
        self.assertEqual(result["externado_reproducibility_batch"], 30)
        self.assertEqual(result["accepted_retrieval_gold"], 0)
        self.assertFalse(result["validation_performance_inspected"])
        self.assertFalse(result["cuda_ready"])

    def test_runner_stays_gated_without_reviewed_gold(self):
        with self.assertRaisesRegex(PermissionError, "BASELINE_GATE_LOCKED"):
            independent_ir_v2.preflight()

    def test_gold_coverage_is_independent_and_metric_populations_are_separate(self):
        rows = [
            {"question_id": "complete", "corpus_coverage": "COMPLETE"},
            {"question_id": "partial", "corpus_coverage": "PARTIAL"},
            {"question_id": "missing", "corpus_coverage": "MISSING"},
            {"question_id": "ambiguous", "corpus_coverage": "AMBIGUOUS"},
        ]
        populations = independent_ir_v2.metric_population(rows)
        self.assertEqual(populations["coverage_n"], 4)
        self.assertEqual(populations["ranking_n"], 1)
        self.assertEqual(populations["coverage_counts"]["MISSING"], 1)
        self.assertEqual(populations["corpus_missing_rate"], 0.25)
        # A missing-corpus gold remains in coverage even though it is ineligible
        # for ranking metrics; corpus presence is not a gold-validity predicate.
        missing_gold = {"question_id": "m", "review_status": "ACCEPTED_RETRIEVAL_GOLD",
                        "minimal_evidence_sets": [["external-source#p1"]],
                        "evidence_sources": [{"source_id": "external-source", "sha256": "a" * 64,
                                             "source_url": "https://official.example/source.pdf"}],
                        "temporal_review_status": "CURRENTLY_SUPPORTABLE", "corpus_coverage": "MISSING"}
        independent_ir_v2.validate_gold_record(missing_gold)

    def test_alternative_minimal_evidence_sets_accept_either_complete_set(self):
        gold = {"minimal_evidence_sets": [["p1"], ["p2", "p3"]],
                "gold_document_ids": ["doc"], "corpus_coverage": "COMPLETE"}
        metric = independent_ir_v2.score(
            [{"passage_id": "p2", "doc_id": "doc"},
             {"passage_id": "p3", "doc_id": "doc"}], gold, {"doc"})
        self.assertEqual(metric["Evidence Completeness@8"], 1.0)

    def test_partial_gold_cannot_be_scored_as_a_ranking_failure(self):
        gold = {"minimal_evidence_sets": [["p1", "p2"]],
                "gold_document_ids": ["doc"], "corpus_coverage": "PARTIAL"}
        with self.assertRaisesRegex(ValueError, "require COMPLETE"):
            independent_ir_v2.score([], gold, {"doc"})


if __name__ == "__main__":
    unittest.main()
