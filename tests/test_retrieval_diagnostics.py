import unittest

from kingscode.retrieval_diagnostics import (
    evidence_completeness,
    fusion_loss,
    graph_recovery_rate,
    oracle_multi_view_recall,
)


class EvidenceDiagnosticTests(unittest.TestCase):
    def test_alternative_evidence_sets_are_not_flattened(self):
        alternatives = [["p1", "p2"], ["p1", "p3"]]
        self.assertEqual(evidence_completeness(["p1", "p3"], alternatives, 2), 1.0)

    def test_oracle_multiview_recall_uses_union_and_alternatives(self):
        self.assertEqual(oracle_multi_view_recall([["p1"], ["p3"]], [["p1", "p2"], ["p1", "p3"]], 2), 1.0)

    def test_fusion_loss_distinguishes_lost_evidence_from_gain(self):
        values = fusion_loss([["p1", "p2"]], ["p1", "x"], [["p1", "p2"]], 2)
        self.assertEqual(values["fusion_loss"], 0.5)
        self.assertEqual(values["fusion_gain"], 0.0)

    def test_graph_recovery_only_denominates_initial_misses(self):
        values = graph_recovery_rate([["p1"], ["p1", "p2"]], [["p1", "p2"], ["p1", "p2"]],
                                     [["p1", "p2"]], 2)
        self.assertEqual(values["initially_incomplete"], 1)
        self.assertEqual(values["recovered_complete"], 1)
        self.assertEqual(values["graph_recovery_rate"], 1.0)

    def test_rejects_empty_or_duplicated_gold_sets(self):
        with self.assertRaises(ValueError):
            evidence_completeness([], [], 2)
        with self.assertRaises(ValueError):
            evidence_completeness([], [["p1", "p1"]], 2)


if __name__ == "__main__":
    unittest.main()
