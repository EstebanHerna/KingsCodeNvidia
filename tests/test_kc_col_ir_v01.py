import sys
import unittest
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import verify_kc_col_ir_v01
import verify_controlled_cuj2026
from tools import independent_ir_v2

def gold_record(qid="q", state="MISSING"):
    return {"question_id": qid, "review_status": "ACCEPTED_RETRIEVAL_GOLD",
            "external_evidence_units": [{"external_evidence_unit_id":"ext-1", "source_id":"official",
                "sha256":"a"*64, "source_url":"https://official.example/doc.pdf", "page":"p.1"}],
            "external_minimal_evidence_sets":[["ext-1"]],
            "corpus_minimal_evidence_sets": [["corpus-p1"]] if state == "COMPLETE" else [],
            "evidence_mapping":{"ext-1":["corpus-p1"] if state == "COMPLETE" else []},
            "evidence_sources":[{"source_id":"official", "sha256":"a"*64, "source_url":"https://official.example/doc.pdf"}],
            "temporal_review_status":"CURRENTLY_SUPPORTABLE", "corpus_coverage":state,
            "gold_document_ids":["doc"] if state == "COMPLETE" else []}

class IndependentBenchmarkTests(unittest.TestCase):
    def test_inventory_and_frozen_sample_are_valid(self):
        result=verify_kc_col_ir_v01.verify()
        self.assertEqual(result["jep_pool"],62)
        self.assertEqual(result["primary_dev_annotation_batch"],30)
        self.assertEqual(result["externado_reproducibility_batch"],30)
        self.assertEqual(result["accepted_retrieval_gold"],10)
        self.assertEqual(result["competitive_corpus_coverage_counts"],{"COMPLETE":0,"PARTIAL":0,"MISSING":10,"AMBIGUOUS":0})
        self.assertEqual(result["controlled_corpus_coverage_counts"],{"COMPLETE":10,"PARTIAL":0,"MISSING":0,"AMBIGUOUS":0})
        self.assertEqual(result["ranking_n"],10)
        self.assertFalse(result["validation_performance_inspected"])
        self.assertFalse(result["cuda_ready"])

    def test_runner_stays_locked_until_explicit_cuda_handoff(self):
        with self.assertRaisesRegex(PermissionError,"CUDA_READY=false"):
            independent_ir_v2.preflight()

    def test_controlled_materialization_is_deterministic_and_all_gold_mappings_resolve(self):
        result=verify_controlled_cuj2026.verify()
        self.assertEqual(result["documents"],6)
        self.assertEqual(result["physical_pages"],191)
        self.assertEqual(result["passages"],190)
        self.assertEqual(result["mapping"]["gold_questions"],10)
        self.assertEqual(result["mapping"]["controlled_complete"],10)
        self.assertEqual(result["competitive_missing"],10)
        self.assertEqual(result["deterministic_rebuild"],"PASS")

    def test_missing_mapped_passage_fails_closed(self):
        gold=verify_controlled_cuj2026.read_jsonl(verify_controlled_cuj2026.BENCH/"gold/dev.jsonl")
        maps=verify_controlled_cuj2026.read_jsonl(verify_controlled_cuj2026.BENCH/"review/controlled_cuj2026_v1_mapping.jsonl")
        coverage=verify_controlled_cuj2026.read_jsonl(verify_controlled_cuj2026.BENCH/"review/controlled_cuj2026_v1_coverage.jsonl")
        docs=verify_controlled_cuj2026.read_jsonl(verify_controlled_cuj2026.BENCH/"review/controlled_cuj2026_v1_documents.jsonl")
        passages=verify_controlled_cuj2026.read_jsonl(verify_controlled_cuj2026.CORPUS/"passages.jsonl")
        passage_id=maps[0]["controlled_passage_ids"][0]
        passages=[p for p in passages if p["passage_id"]!=passage_id]
        with self.assertRaisesRegex(ValueError,"Mapped passage absent"):
            verify_controlled_cuj2026.validate_mappings(gold,maps,coverage,passages,docs)

    def test_ranking_readiness_requires_passage_file(self):
        coverage=[{"question_id":f"q{i}","controlled_corpus_coverage":"COMPLETE"} for i in range(10)]
        self.assertEqual(verify_controlled_cuj2026.ranking_readiness(coverage,False),
                         {"controlled_complete_coverage_n":10,"ranking_n":0,"unlocked":False})
        self.assertEqual(verify_controlled_cuj2026.ranking_readiness(coverage,True),
                         {"controlled_complete_coverage_n":10,"ranking_n":10,"unlocked":True})

    def test_manifest_gates_are_unlocked_but_cuda_is_not_claimed(self):
        manifest=json.loads((verify_kc_col_ir_v01.BENCH/"manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(manifest["gold_gate"]["unlocked"])
        self.assertTrue(manifest["ranking_gate"]["unlocked"])
        self.assertEqual(manifest["ranking_gate"]["ranking_n"],10)
        self.assertTrue(manifest["retrieval_benchmark_ready"])
        self.assertFalse(manifest["cuda_ready"])

    def test_controlled_ranking_population_is_separate_from_competitive_coverage(self):
        gold=[{"question_id":f"q{i}","corpus_coverage":"MISSING"} for i in range(10)]
        controlled=[{"question_id":f"q{i}","controlled_corpus_coverage":"COMPLETE"} for i in range(10)]
        self.assertEqual(independent_ir_v2.metric_population(gold,"competitive_corpus_v01")["ranking_n"],0)
        self.assertEqual(independent_ir_v2.metric_population(gold,"controlled_cuj2026_v1",controlled)["ranking_n"],10)

    def test_30_candidates_10_accepted_and_20_pending_pass_gold_subset_gate(self):
        candidates=[{"question_id":f"q{i}", "review_status":"PENDING_PRIMARY_EVIDENCE", "temporal_review_status":"UNCERTAIN"} for i in range(30)]
        gold=[gold_record(f"q{i}") for i in range(10)]
        selected, by_id=independent_ir_v2.select_evaluation_subset(candidates,gold)
        self.assertEqual(len(selected),10)
        self.assertEqual(set(by_id),{f"q{i}" for i in range(10)})
        self.assertEqual(len(candidates),30)

    def test_hydration_uses_exact_hash_checked_source_pool_wording(self):
        pool_path=ROOT/"tmp/kc_col_ir_v0.1/pool/jep_cuj_2026_full_pool.jsonl"
        pool=[__import__("json").loads(line) for line in pool_path.read_text(encoding="utf-8").splitlines()]
        item=next(row for row in pool if row["source_item_number"]=="9")
        candidate={"question_id":"JEP-CUJ-2026-Q009", "source_item_number":"9", "question_text_sha256":__import__("hashlib").sha256(item["question_text"].encode("utf-8")).hexdigest()}
        hydrated=independent_ir_v2.hydrate_candidate_questions([candidate],pool)
        self.assertEqual(hydrated[0]["question"],item["question_text"])

    def test_subset_rejects_duplicate_and_noncandidate_gold_ids(self):
        candidates=[{"question_id":"q1"}]
        with self.assertRaisesRegex(ValueError,"Duplicate gold"):
            independent_ir_v2.select_evaluation_subset(candidates,[gold_record("q1")]*2)
        duplicate_candidates=[{"question_id":"q1"},{"question_id":"q1"}]
        with self.assertRaisesRegex(ValueError,"Duplicate frozen"):
            independent_ir_v2.select_evaluation_subset(duplicate_candidates,[gold_record("q1")])
        candidates=[{"question_id":f"q{i}"} for i in range(10)]
        with self.assertRaisesRegex(ValueError,"not a frozen candidate"):
            independent_ir_v2.select_evaluation_subset(candidates,[gold_record(f"outside{i}") for i in range(10)])

    def test_gold_coverage_and_ranking_populations_are_separate(self):
        rows=[{"question_id":"c","corpus_coverage":"COMPLETE"},{"question_id":"p","corpus_coverage":"PARTIAL"},{"question_id":"m","corpus_coverage":"MISSING"},{"question_id":"a","corpus_coverage":"AMBIGUOUS"}]
        pop=independent_ir_v2.metric_population(rows)
        self.assertEqual(pop["coverage_n"],4);self.assertEqual(pop["ranking_n"],1)
        self.assertEqual(pop["coverage_counts"]["MISSING"],1);self.assertEqual(pop["corpus_missing_rate"],0.25)
        independent_ir_v2.validate_gold_record(gold_record("missing","MISSING"))

    def test_nine_gold_stays_below_minimum_but_ten_unlocks_gold_threshold(self):
        self.assertLess(9, independent_ir_v2.MIN_GOLD)
        self.assertGreaterEqual(10, independent_ir_v2.MIN_GOLD)
        candidates=[{"question_id":f"q{i}"} for i in range(9)]
        with self.assertRaisesRegex(PermissionError,"GOLD_GATE_LOCKED"):
            independent_ir_v2.select_evaluation_subset(candidates,[gold_record(f"q{i}") for i in range(9)])

    def test_external_evidence_ids_never_enter_corpus_ranking_metrics(self):
        gold=gold_record("q","COMPLETE")
        metric=independent_ir_v2.score([{"passage_id":"ext-1","doc_id":"doc"}],gold,{"doc"})
        self.assertEqual(metric["Evidence Completeness@8"],0.0)
        self.assertEqual(metric["Recall@10"],0.0)
        metric=independent_ir_v2.score([{"passage_id":"corpus-p1","doc_id":"doc"}],gold,{"doc"})
        self.assertEqual(metric["Evidence Completeness@8"],1.0)

    def test_alternative_minimal_corpus_sets_accept_either_complete_set(self):
        gold=gold_record("q","COMPLETE");gold["corpus_minimal_evidence_sets"]=[["p1"],["p2","p3"]]
        metric=independent_ir_v2.score([{"passage_id":"p2","doc_id":"doc"},{"passage_id":"p3","doc_id":"doc"}],gold,{"doc"})
        self.assertEqual(metric["Evidence Completeness@8"],1.0)

    def test_partial_gold_cannot_be_scored_as_ranking_failure(self):
        with self.assertRaisesRegex(ValueError,"require COMPLETE"):
            independent_ir_v2.score([],gold_record("q","PARTIAL"),{"doc"})

    def test_evidence_completeness_at_8_is_fractional_not_binary(self):
        gold = gold_record("q", "COMPLETE")
        gold["corpus_minimal_evidence_sets"] = [["p1", "p2", "p3", "p4"]]
        ranked = [{"passage_id": "p1", "doc_id": "doc"}, {"passage_id": "p2", "doc_id": "doc"}]
        metric = independent_ir_v2.score(ranked, gold, {"doc"})
        self.assertAlmostEqual(metric["Evidence Completeness@8"], 0.5)
        self.assertEqual(metric["Complete Evidence Set@8"], 0.0)

    def test_complete_evidence_set_at_8_stays_binary(self):
        gold = gold_record("q", "COMPLETE")
        gold["corpus_minimal_evidence_sets"] = [["p1", "p2", "p3", "p4"]]
        ranked = [{"passage_id": f"p{i}", "doc_id": "doc"} for i in range(1, 5)]
        metric = independent_ir_v2.score(ranked, gold, {"doc"})
        self.assertEqual(metric["Evidence Completeness@8"], 1.0)
        self.assertEqual(metric["Complete Evidence Set@8"], 1.0)

    def test_evidence_completeness_uses_best_alternative_set(self):
        gold = gold_record("q", "COMPLETE")
        gold["corpus_minimal_evidence_sets"] = [["p1", "p2", "p3", "p4"], ["p5", "p6"]]
        ranked = [{"passage_id": "p5", "doc_id": "doc"}, {"passage_id": "p6", "doc_id": "doc"}]
        metric = independent_ir_v2.score(ranked, gold, {"doc"})
        self.assertEqual(metric["Evidence Completeness@8"], 1.0)
        self.assertEqual(metric["Complete Evidence Set@8"], 1.0)

if __name__=="__main__": unittest.main()
