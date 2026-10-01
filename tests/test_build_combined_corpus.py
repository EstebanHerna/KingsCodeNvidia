"""Combined corpus v0.1 + v0.2: concatenation only, inputs untouched, A's Retriever opens it."""
from pathlib import Path
import shutil
import tempfile
import unittest

from kingscode.common import ROOT, file_hash, indexable, read_json, write_json, write_jsonl
from kingscode.retrieval import BM25Index, Retriever
from tools.build_combined_corpus import combine

V02 = ROOT / "corpora/corpus-v0.2"


def mini_base(directory: Path) -> None:
    passages = read_json(ROOT / "tests/fixtures/member_b_official_passages.json")
    write_jsonl(directory / "passages.jsonl", passages)
    write_jsonl(directory / "graph/nodes.jsonl", [])
    write_jsonl(directory / "graph/edges.jsonl", [])
    BM25Index([p for p in passages if indexable(p)]).save(directory / "index/bm25.json", file_hash(directory / "passages.jsonl"))
    write_json(directory / "manifest.json", {"version": "fixture-base", "documentos": [{"doc_id": p["doc_id"]} for p in passages],
                                             "hashes": {"passages.jsonl": file_hash(directory / "passages.jsonl")}})


class CombinedCorpusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=ROOT))
        mini_base(self.tmp / "base")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_combines_without_touching_inputs_and_retriever_opens_it(self):
        before = {p: file_hash(p) for p in V02.rglob("*") if p.is_file()}
        manifest = combine(self.tmp / "base", V02, self.tmp / "out")
        self.assertEqual(before, {p: file_hash(p) for p in V02.rglob("*") if p.is_file()})
        self.assertEqual(manifest["n_fragmentos"], 5 + read_json(V02 / "manifest.json")["n_passages"])
        retriever = Retriever(self.tmp / "out", mode="bm25")
        ids = [p["passage_id"] for p in retriever.retrieve("Decreto 046 de 2024", k=8, graph_mode="off")]
        self.assertTrue(any(i.startswith("decreto_046_de_2024") for i in ids))

    def test_overlap_and_existing_output_are_refused(self):
        with self.assertRaises(ValueError):
            combine(self.tmp / "base", self.tmp / "base", self.tmp / "dup")
        combine(self.tmp / "base", V02, self.tmp / "out")
        with self.assertRaises(FileExistsError):
            combine(self.tmp / "base", V02, self.tmp / "out")

    def test_relative_repo_paths_are_recorded_portably(self):
        workspace = Path(tempfile.mkdtemp(dir=ROOT))
        try:
            mini_base(workspace / "base")
            relative_workspace = workspace.relative_to(ROOT)
            manifest = combine(relative_workspace / "base", V02.relative_to(ROOT), relative_workspace / "out")
            runtime_manifest = read_json(workspace / "out/manifest.json")
            self.assertEqual(manifest["status"], "diagnostic_not_competitive_freeze")
            self.assertEqual(set(runtime_manifest["inputs"]), {relative_workspace.joinpath("base").as_posix(), "corpora/corpus-v0.2"})
        finally:
            shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
