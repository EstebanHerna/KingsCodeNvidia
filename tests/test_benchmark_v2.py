from pathlib import Path
import tempfile
from unittest.mock import patch
import unittest
from jsonschema import Draft202012Validator, ValidationError
from kingscode.common import ROOT, read_json, read_jsonl, write_json, write_jsonl, file_hash
from kingscode import benchmark_v2 as v2


def fixtures():
    return [{"passage_id": f"fixture-{i:02d}", "doc_id": f"fixture-{i:02d}",
             "canonical_body": ["ley", str(i+100), "2000"], "article": "1", "norm_name": f"Ley {i+100} de 2000",
             "text": f"ARTÍCULO 1. <CAPTION FIXTURE {i:02d}>\nMechanical test body.", "text_prefix": "",
             "clean_start": 0, "clean_end": 60, "source_url": "https://example.test/fixture",
             "source_sha256": "fixture", "areas": [f"fixture-area-{i%4}"]} for i in range(16)]


class BenchmarkV2Tests(unittest.TestCase):
    def test_determinism_and_family_split_isolation(self):
        a=v2.pilot_records(fixtures()); b=v2.pilot_records(list(reversed(fixtures())))
        self.assertEqual(a,b)
        docs={s:{x[2]["canonical_document_id"] for x in rows} for s,rows in a.items()}
        self.assertFalse(docs['dev'] & docs['validation'] or docs['dev'] & docs['holdout'] or docs['validation'] & docs['holdout'])
        self.assertEqual([len(a[s]) for s in ('dev','validation','holdout')],[6,3,3])

    def test_no_answer_or_provenance_in_question_schema(self):
        validator=Draft202012Validator(read_json(v2.DIRECTORY/'question.schema.json'))
        q=v2.pilot_records(fixtures())['dev'][0][0]
        for key in ('expected_answer','legal_basis','gold_document_ids','source_url','canonical_fragment_id'):
            with self.assertRaises(ValidationError): validator.validate(dict(q,**{key:'forbidden'}))

    def test_extractive_concept_not_model_authored(self):
        for rows in v2.pilot_records(fixtures()).values():
            for q,g,p in rows:
                self.assertNotIn('expected_answer',g)
                if q['category']=='CONCEPT': self.assertEqual(q['question'],p['caption'])

    def test_gold_only_after_all_rankings_and_only_text_backend(self):
        bundle=v2.pilot_records(fixtures())['dev'];calls=[];original=read_jsonl
        with tempfile.TemporaryDirectory() as td:
            directory=Path(td)
            write_json(directory/'manifest.json',{'corpus_sha256':'fixture'})
            write_jsonl(directory/'questions/dev.jsonl',[r[0] for r in bundle])
            write_jsonl(directory/'gold/dev.jsonl',[r[1] for r in bundle])
            def reader(path):
                if path.parent.name=='gold': self.assertEqual(len(calls),6)
                self.assertNotIn('holdout',path.name)
                return original(path)
            def retrieve(text,k,mode):
                self.assertIsInstance(text,str);calls.append(text);return []
            with patch.object(v2,'check'),patch.object(v2,'file_hash',return_value='fixture'),patch.object(v2,'read_jsonl',side_effect=reader):
                result=v2.evaluate_dev(retrieve,directory,directory)
            self.assertFalse(result['holdout_executed'])
            self.assertEqual(len(result['per_question']),6)

    def test_check_hashes_but_never_parses_sealed_holdout(self):
        original=v2.read_jsonl
        def reader(path):
            self.assertNotIn('holdout',path.name)
            self.assertNotEqual(path.parent.name,'gold')
            return original(path)
        with patch.object(v2,'read_jsonl',side_effect=reader):
            self.assertFalse(v2.check()['holdout_parsed'])

    def test_gold_schema_supports_alternative_minimal_evidence_sets(self):
        validator=Draft202012Validator(read_json(v2.DIRECTORY/'gold.schema.json'))
        valid={"id":"KC2-TEST-001","record_type":"RETRIEVAL_GOLD","annotation":"reviewed",
               "gold_document_ids":["ley:1:2000"],"gold_fragment_ids":["ley:1:2000:articulo:1","ley:1:2000:articulo:2"],
               "evidence":[{"canonical_fragment_id":"ley:1:2000:articulo:1","relevance":"direct"},
                           {"canonical_fragment_id":"ley:1:2000:articulo:2","relevance":"direct"}],
               "minimal_evidence_sets":[
                   [{"canonical_fragment_id":"ley:1:2000:articulo:1","relevance":"direct"}],
                   [{"canonical_fragment_id":"ley:1:2000:articulo:2","relevance":"direct"}]],
               "gold_spans":[{"canonical_fragment_id":"ley:1:2000:articulo:1","passage_id":"p1","clean_start":0,"clean_end":4}]}
        validator.validate(valid)
        end_to_end={"id":"KC2-TEST-002","record_type":"END_TO_END_ONLY","annotation":"answer checked against official source","answer_source":"official source page"}
        validator.validate(end_to_end)
        with self.assertRaises(ValidationError):
            validator.validate({"id":"KC2-TEST-003","record_type":"RETRIEVAL_GOLD","annotation":"missing alternatives"})

    def test_complete_evidence_set_accepts_either_alternative(self):
        gold={"minimal_evidence_sets":[
            [{"canonical_fragment_id":"fragment-a","relevance":"direct"}],
            [{"canonical_fragment_id":"fragment-b","relevance":"direct"},
             {"canonical_fragment_id":"fragment-c","relevance":"supporting"}]]}
        first=[{"canonical_fragment_id":"fragment-a"}]
        second=[{"canonical_fragment_id":"fragment-b"},{"canonical_fragment_id":"fragment-c"}]
        incomplete=[{"canonical_fragment_id":"fragment-b"}]
        self.assertEqual(v2.complete_evidence_set_at_k(first,gold,8),1)
        self.assertEqual(v2.complete_evidence_set_at_k(second,gold,8),1)
        self.assertEqual(v2.complete_evidence_set_at_k(incomplete,gold,8),0)

    def test_immutable_builder(self):
        with self.assertRaises(FileExistsError): v2.build(ROOT/'corpus')


if __name__=='__main__':unittest.main()
