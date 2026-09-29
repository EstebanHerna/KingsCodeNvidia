import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import verify_kc_col_ir_v01
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
        self.assertEqual(result["accepted_retrieval_gold"],9)
        self.assertEqual(result["corpus_coverage_counts"],{"COMPLETE":0,"PARTIAL":0,"MISSING":9,"AMBIGUOUS":0})
        self.assertEqual(result["ranking_n"],0)
        self.assertFalse(result["validation_performance_inspected"])
        self.assertFalse(result["cuda_ready"])

    def test_runner_stays_locked_below_gold_gate(self):
        with self.assertRaisesRegex(PermissionError,"GOLD_GATE_LOCKED"):
            independent_ir_v2.preflight()

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

if __name__=="__main__": unittest.main()
