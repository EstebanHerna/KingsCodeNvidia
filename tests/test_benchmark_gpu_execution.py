"""CPU fixtures only: no model/network/CUDA execution in this suite."""
import copy
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch, Mock

from kingscode.common import ROOT, file_hash, read_json, write_json
from kingscode import retrieval_benchmark as bench
from kingscode import benchmark_runtime as runtime
from kingscode import benchmark_analysis as analysis
from test_retrieval_benchmark import p, gold


class VariantTests(unittest.TestCase):
    def test_dense_only(self):
        c = runtime.variant_config("R1-QWEN")
        self.assertEqual((c["mode"], c["graph_mode"], c["rerank"]), ("dense", "off", False))
        self.assertEqual(runtime.NoLexicalRanking().ranking("safe", 30), ([], {}))

    def test_hybrid(self):
        c = runtime.variant_config("R2-QWEN")
        self.assertEqual((c["mode"], c["graph_mode"], c["rerank"]), ("hybrid", "off", False))
        self.assertEqual((c["candidate_k"], c["rrf_constant"]), (30, 60))

    def test_r3(self):
        c = runtime.variant_config("R3")
        self.assertEqual((c["mode"], c["graph_mode"], c["rerank"]), ("hybrid", "off", True))

    def test_graph_only_drift(self):
        for variant, mode in (("R4", "auto"), ("R5", "on")):
            expected = runtime.variant_config("R3")
            expected["graph_mode"] = mode
            self.assertEqual(runtime.variant_config(variant), expected)

    def test_metadata_uses_r3_and_existing_functions(self):
        for variant in ("R6", "R7", "R8"):
            config = runtime.variant_config(variant)
            self.assertTrue(config["rerank"])
            self.assertEqual(config["mode"], "hybrid")
            rt = runtime.NeuralRuntime.__new__(runtime.NeuralRuntime)
            rt.config, rt.retriever = config, object()
            with patch("kingscode.metadata_experiments.run_experiment", return_value=[]) as call:
                rt.retrieve("safe", 30)
                call.assert_called_once_with(variant, rt.retriever, "safe", 30, **config["effective_parameters"])

    def test_auto_routes_on_flat_evidence_without_rewriting_question(self):
        from kingscode.reasoning.routing import RetrieverGraphRouter
        rt = runtime.NeuralRuntime.__new__(runtime.NeuralRuntime)
        rt.config = runtime.variant_config("R4")
        rt.adapter, rt.retriever = RetrieverGraphRouter(), Mock()
        rt.retriever.retrieve.return_value = []
        with patch("kingscode.reasoning.routing.route_graph", return_value="on") as router:
            rt.retrieve("safe", 30)
        self.assertEqual(rt.retriever.retrieve.call_args_list[0].args, ("safe", 30, "off"))
        self.assertEqual(rt.retriever.retrieve.call_args_list[1].args, ("safe", 30, "auto"))
        router.assert_called_once_with("safe", [])
        self.assertTrue(rt.adapter("safe"))

    def test_bge_has_no_executable_registration(self):
        for v in ("R1-BGE", "R2-BGE"):
            self.assertNotIn(v, runtime.EXECUTABLE)
            with self.assertRaises(ValueError): runtime.variant_config(v)


class PrerequisiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        (self.path / "index").mkdir()
        self.config = read_json(ROOT / "config/neural.json")
        self.config.update(device="cuda:0", dtype="bfloat16")

    def tearDown(self): self.tmp.cleanup()

    def preflight(self):
        with patch("kingscode.neural.configuration", return_value=self.config):
            return runtime.preflight(self.path, runtime.variant_config("R1-QWEN"))

    def test_missing_dense_explicit(self):
        with self.assertRaisesRegex(FileNotFoundError, "dense.npy"): self.preflight()

    def test_missing_snapshot_explicit(self):
        for name in ("dense.npy", "dense.meta.json"):
            (self.path / "index" / name).write_bytes(b"fixture")
        with patch.object(runtime, "verify_snapshot", side_effect=FileNotFoundError("MODEL_NOT_PREPARED")):
            with self.assertRaisesRegex(FileNotFoundError, "MODEL_NOT_PREPARED"): self.preflight()

    def test_cpu_config_rejected(self):
        self.config["device"] = "cpu"
        with self.assertRaisesRegex(RuntimeError, "CUDA_REQUIRED"): self.preflight()

    def test_cuda_availability_required(self):
        from kingscode.neural import setup
        torch = Mock()
        torch.cuda.is_available.return_value = False
        with patch.dict("sys.modules", {"torch": torch}):
            with self.assertRaisesRegex(RuntimeError, "CUDA requested"): setup(self.config)

    def test_no_download_or_substitution(self):
        for key, val in (("local_files_only", False), ("embedding_model", "BAAI/bge-m3")):
            cfg = dict(self.config, **{key: val})
            with patch("kingscode.neural.configuration", return_value=cfg):
                with self.assertRaises(ValueError): runtime.preflight(self.path, runtime.variant_config("R1-QWEN"))

    def test_fake_backend_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "UNVERIFIED_BACKEND"):
            runtime.verify_loaded_backend(object(), runtime.variant_config("R3"), Mock())

    def test_provenance_uses_executed_settings(self):
        assets = {"neural_config": self.config, "dense_sha256": "vectors", "dense_meta_sha256": "meta",
                  "models": {"encoder": {"repo_id": "qwen", "revision": "fixed", "manifest_sha256": "files", "snapshot": "host-path"}}}
        result = runtime.execution_identity(runtime.variant_config("R4"), assets, {"code": "hash"})
        self.assertEqual(result["neural_config"]["device"], "cuda:0")
        self.assertEqual(result["models"]["encoder"]["manifest_sha256"], "files")
        self.assertNotIn("snapshot", result["models"]["encoder"])


class BoundaryTests(unittest.TestCase):
    def test_every_ranking_precedes_gold_and_replays(self):
        passage = p("p", "law_1", "1")
        qs = [{"id": str(i), "question": "safe " + str(i), "area": "civil", "tags": [], "format": "retrieval"} for i in range(2)]
        events = []
        def retrieve(text, k, mode):
            self.assertIsInstance(text, str)
            events.append(text)
            return [copy.deepcopy(passage)]
        def labels(split):
            self.assertEqual(events[-2:], ["safe 0", "safe 1"])
            return {q["id"]: gold([passage]) for q in qs}
        with tempfile.TemporaryDirectory() as td, patch.object(bench, "_assert_clean_tree"), \
             patch.object(bench, "_verify_declared_hashes"), patch.object(bench, "_safe_questions", return_value=qs), \
             patch.object(bench, "_gold_after_ranking", side_effect=labels), patch.object(bench, "Retriever") as retriever:
            retriever.return_value.retrieve.side_effect = retrieve
            a = bench.run("R0", "dev", output_root=Path(td))
            b = bench.run("R0", "dev", output_root=Path(td))
        self.assertEqual(a["status"], "passed")
        for name in ("Recall@10", "Evidence Completeness@8", "MRR@10"):
            self.assertEqual(a["metrics"][name], b["metrics"][name])

    def test_neural_failure_cannot_report_passed_or_read_gold(self):
        with tempfile.TemporaryDirectory() as td, patch.object(bench, "_assert_clean_tree"), \
             patch.object(bench, "_verify_declared_hashes"), patch.object(runtime, "NeuralRuntime", side_effect=RuntimeError("CUDA_REQUIRED")), \
             patch.object(bench, "_gold_after_ranking") as labels:
            result = bench.run("R1-QWEN", "dev", output_root=Path(td))
        self.assertEqual(result["status"], "failed")
        self.assertNotIn("metrics", result)
        labels.assert_not_called()

    def test_consumed_r0_holdout_stays_closed(self):
        with self.assertRaises(PermissionError):
            bench.run("R0", "holdout", allow_holdout=True, holdout_purpose="predeclared_baseline")

    def test_base_requires_validation_and_real_weights(self):
        with self.assertRaises(ValueError): runtime.validate_base_run(None, "sha", {})
        fake = {"variant": "R2-QWEN", "split": "dev", "benchmark": {"manifest_sha256": "sha"}, "corpus": {}}
        with patch.object(analysis, "load_run", return_value=(fake, [])):
            with self.assertRaises(ValueError): runtime.validate_base_run(Path("fake"), "sha", {})

    def test_duplicate_ids_complementarity_rejected(self):
        with self.assertRaises(ValueError): bench.complementarity([{"id": "a"}, {"id": "a"}], [{"id": "a"}])

    def test_fixed_manifest_and_official_files(self):
        self.assertEqual(file_hash(ROOT / "benchmarks/kingscode_ir/manifests/benchmark_manifest.json"),
                         "326a405748dd20f641d5cf4103ceaafb6a19f07b43db54d95f472a2b439e3071")
        import subprocess
        for path in ("data", "schema", "scripts", "benchmarks/kingscode_ir", "config/models.lock.json"):
            diff = subprocess.check_output(["git", "diff", "a3548a1", "--", path], cwd=ROOT)
            self.assertEqual(diff, b"")

    def test_selection_rejects_dev_and_diagnostic(self):
        for split, diagnostic in (("dev", False), ("validation", True)):
            report = {"variant": "R0", "split": split, "config": {"diagnostic": diagnostic},
                      "benchmark": {"manifest_sha256": bench.benchmark_identity()["manifest_sha256"]}}
            with patch.object(analysis, "load_run", return_value=(report, [{"id": "a"}])):
                with self.assertRaises(ValueError):
                    analysis.record_selection([Path("a"), Path("b")], variant=None, rationale="inconclusive")

    def test_neural_rankings_precede_gold_with_only_text_input(self):
        qs = [{"id": str(i), "question": "safe " + str(i), "area": "civil", "tags": [], "format": "retrieval"} for i in range(2)]
        events = []
        backend = Mock()
        backend.record.return_value = {"verified_real_backend": True, "hardware": {}, "peak_vram_bytes": 1}
        backend.assets = {"models": {}}
        def retrieve(text, k):
            self.assertIsInstance(text, str)
            events.append(text)
            return [p("p", "law_1", "1")]
        backend.retrieve.side_effect = retrieve
        def labels(split):
            self.assertEqual(events, ["safe 0", "safe 1"])
            return {q["id"]: gold([p("p", "law_1", "1")]) for q in qs}
        with tempfile.TemporaryDirectory() as td, patch.object(bench, "_assert_clean_tree"), \
             patch.object(bench, "_verify_declared_hashes"), patch.object(bench, "_safe_questions", return_value=qs), \
             patch.object(runtime, "NeuralRuntime", return_value=backend), \
             patch.object(runtime, "execution_identity", return_value={"fixture": True}), \
             patch.object(bench, "_gold_after_ranking", side_effect=labels):
            result = bench.run("R1-QWEN", "dev", output_root=Path(td))
        self.assertEqual(result["status"], "passed")  # fixture artifact deleted with TemporaryDirectory

    def test_false_verification_flag_rejects_before_rankings(self):
        backend = Mock()
        backend.record.return_value = {"verified_real_backend": False}
        with tempfile.TemporaryDirectory() as td, patch.object(bench, "_assert_clean_tree"), \
             patch.object(bench, "_verify_declared_hashes"), patch.object(runtime, "NeuralRuntime", return_value=backend):
            result = bench.run("R1-QWEN", "dev", output_root=Path(td))
        self.assertEqual(result["status"], "failed")
        backend.retrieve.assert_not_called()
        self.assertNotIn("metrics", result)

    def test_holdout_rejects_output_override_and_selection_mismatch(self):
        with self.assertRaises(PermissionError):
            bench.run("R3", "holdout", output_root=Path("custom"), allow_holdout=True,
                      holdout_purpose="post_selection_confirmation")
        with tempfile.TemporaryDirectory() as td, patch.object(bench, "ROOT", Path(td)), \
             patch.object(bench, "_holdout_declaration", return_value={"benchmark_manifest_sha256": "sha"}), \
             patch.object(bench, "_holdout_was_consumed", return_value=False):
            path = Path(td) / "reports/benchmark/selection/selected_config.json"
            valid = {"status": "selected", "selection_split": "validation", "variant": "R3", "benchmark_manifest_sha256": "sha"}
            for key, wrong in (("status", "no_selection"), ("selection_split", "dev"), ("variant", "R4"), ("benchmark_manifest_sha256", "other")):
                write_json(path, dict(valid, **{key: wrong}))
                with self.assertRaises(PermissionError):
                    bench._assert_holdout_policy("holdout", "R3", True, "post_selection_confirmation")
            write_json(path, valid)
            bench._assert_holdout_policy("holdout", "R3", True, "post_selection_confirmation")

    def test_selection_no_selection_and_explicit_immutable_choice(self):
        manifest = bench.benchmark_identity()["manifest_sha256"]
        baseline = {"variant": "R0", "split": "validation", "corpus": {}, "config": {},
                    "benchmark": {"manifest_sha256": manifest}, "metrics": {}, "subgroups": {},
                    "execution_identity": {"fixture": "r0"}}
        candidate = dict(baseline, variant="R1-QWEN", execution={"verified_real_backend": True},
                         execution_identity={"fixture": "qwen"})
        def load(path): return (baseline if path.name == "r0" else candidate), [{"id": "a"}]
        with tempfile.TemporaryDirectory() as td, patch.object(analysis, "ROOT", Path(td)), \
             patch.object(analysis, "load_run", side_effect=load), patch.object(analysis, "file_hash", return_value="hash"), \
             patch.object(analysis, "bootstrap_reports", return_value={"fixture": True}):
            paths = [Path("r0"), Path("qwen")]
            result = analysis.record_selection(paths, variant=None, rationale="inconclusive")
            self.assertEqual(result["status"], "no_selection")
            result = analysis.record_selection(paths, variant="R1-QWEN", rationale="explicit reviewed trade-off")
            self.assertEqual(result["execution_identity"], candidate["execution_identity"])
            self.assertFalse(result["holdout_executed"])
            with self.assertRaises(FileExistsError):
                analysis.record_selection(paths, variant=None, rationale="retuning forbidden")


if __name__ == "__main__":
    unittest.main()
