import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import verify_kc_col_ir_v01
from tools import independent_ir_v2


class IndependentBenchmarkTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / "tmp/kc_col_ir_v0.1/pool/externado_procesal_full_pool.jsonl").exists(),
                         "local frozen full-pool artifact (tmp/, not in git) required")
    def test_inventory_and_deterministic_sample_are_valid(self):
        result = verify_kc_col_ir_v01.verify()
        self.assertEqual(result["externado_pool"], 270)
        self.assertEqual(result["dev_annotation_batch"], 30)
        self.assertEqual(result["accepted_retrieval_gold"], 0)
        self.assertFalse(result["validation_performance_inspected"])
        self.assertFalse(result["cuda_ready"])

    def test_runner_stays_gated_without_reviewed_gold(self):
        with self.assertRaisesRegex(PermissionError, "BASELINE_GATE_LOCKED"):
            independent_ir_v2.preflight()


if __name__ == "__main__":
    unittest.main()
