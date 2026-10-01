import unittest
from pathlib import Path
from unittest.mock import patch

from tools import verify_kc_col_ir_target_handoff as handoff


class TargetHandoffTests(unittest.TestCase):
    def setUp(self):
        self.diagnostic_path = Path("diagnostic.json")
        self.smoke_path = Path("smoke.json")
        self.audit_path = Path("audit.json")
        self.hashes = {
            "manifest.json": "a" * 64,
            "questions/dev.jsonl": "b" * 64,
            "gold/dev.jsonl": "c" * 64,
            "pool/jep_cuj_2026_full_pool.jsonl": "d" * 64,
            "controlled_cuj2026_v1_profile.json": "e" * 64,
            "passages.jsonl": "f" * 64,
            "diagnostic.json": "1" * 64,
            "smoke.json": "2" * 64,
            "audit.json": "3" * 64,
            "expediente_concurso_jep_2026.zip": "3f9dc1765e8ea18588c13a48e1785b506f6a0c06eef3743057e2d34097d9b101",
            "expediente_2026_acquisition.json": "4" * 64,
        }
        self.revisions = handoff.EXPECTED.copy()
        self.data = {
            "manifest.json": {"baseline_gate": {"unlocked": True}},
            "sampling_manifest.json": {"pool_artifact_sha256": "d" * 64},
            "expediente_2026_acquisition.json": {
                "archive": {"sha256": self.hashes["expediente_concurso_jep_2026.zip"]},
                "member_count": 18, "members": [{} for _ in range(18)],
            },
            self.diagnostic_path.name: {
                "gpus": [{"name": "NVIDIA GeForce RTX 4090"}],
                "torch": {"cuda_available": True, "bf16_supported": True, "devices": []},
            },
            self.smoke_path.name: {
                "status": "passed", "model": "qwen3-8b",
                "runtime": {"gpu": "NVIDIA GeForce RTX 4090"},
                "stages": [{"stage": stage} for stage in ("bf16_matmul", "embedding", "reranker", "decoder_and_guards")],
                "assets": [{"repo_id": repo, "revision": rev} for repo, rev in self.revisions.items()],
            },
            self.audit_path.name: {
                "status": "PASS", "identity": {
                    "benchmark_manifest_sha256": self.hashes["manifest.json"],
                    "question_manifest_sha256": self.hashes["questions/dev.jsonl"],
                    "gold_sha256": self.hashes["gold/dev.jsonl"],
                    "controlled_profile_sha256": self.hashes["controlled_cuj2026_v1_profile.json"],
                    "controlled_passages_sha256": self.hashes["passages.jsonl"],
                    "encoder": {"revision": self.revisions["Qwen/Qwen3-Embedding-0.6B"]},
                    "reranker": {"revision": self.revisions["Qwen/Qwen3-Reranker-0.6B"]},
                },
            },
        }

    def patches(self):
        def fake_hash(path):
            p = Path(path)
            normalized = p.as_posix().replace("\\", "/")
            if normalized.endswith("/manifest.json"):
                return self.hashes["manifest.json"]
            if normalized.endswith("/questions/dev.jsonl"):
                return self.hashes["questions/dev.jsonl"]
            if normalized.endswith("/gold/dev.jsonl"):
                return self.hashes["gold/dev.jsonl"]
            if normalized.endswith("/jep_cuj_2026_full_pool.jsonl"):
                return self.hashes["pool/jep_cuj_2026_full_pool.jsonl"]
            if normalized.endswith("/expediente_concurso_jep_2026.zip"):
                return self.hashes["expediente_concurso_jep_2026.zip"]
            if normalized.endswith("/controlled_cuj2026_v1_profile.json"):
                return self.hashes["controlled_cuj2026_v1_profile.json"]
            if normalized.endswith("/passages.jsonl"):
                return self.hashes["passages.jsonl"]
            return self.hashes.get(p.name, "0" * 64)

        return (
            patch.object(handoff, "BENCH", Path("bench")),
            patch.object(handoff, "ROOT", Path("root")),
            patch.object(handoff, "read_json", side_effect=lambda p: self.data[Path(p).name]),
            patch.object(handoff, "file_hash", side_effect=fake_hash),
            patch.object(handoff.benchmark, "read_jsonl", return_value=[]),
            patch.object(handoff.benchmark, "verify_controlled_profile_files"),
        )

    def test_target_handoff_accepts_matching_passed_evidence(self):
        with self.patches()[0], self.patches()[1], self.patches()[2], self.patches()[3], self.patches()[4], self.patches()[5]:
            report = handoff.verify(self.diagnostic_path, self.smoke_path, self.audit_path)
        self.assertEqual(report["status"], "PASS")
        self.assertFalse(report["retrieval_executed"])

    def test_failed_smoke_does_not_unlock_target_handoff(self):
        self.data[self.smoke_path.name]["status"] = "failed"
        with self.patches()[0], self.patches()[1], self.patches()[2], self.patches()[3], self.patches()[4], self.patches()[5]:
            with self.assertRaisesRegex(ValueError, "GPU smoke must pass"):
                handoff.verify(self.diagnostic_path, self.smoke_path, self.audit_path)

    def test_failed_saved_handoff_is_rejected(self):
        with patch.object(handoff, "read_json", return_value={"status": "FAILED", "retrieval_executed": False}):
            with self.assertRaisesRegex(PermissionError, "not a verified"):
                handoff.verify_saved_handoff(Path(__file__))


if __name__ == "__main__":
    unittest.main()
