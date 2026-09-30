"""Corpus snapshot packaging on a synthetic fixture corpus (never the real corpus bytes)."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import package_corpus_snapshot as pkg  # noqa: E402

TMP = ROOT / "tmp/package_snapshot"


def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fixture_repo(base: Path) -> Path:
    corpus = base / "corpus"
    files = {"passages.jsonl": b'{"passage_id": "p1"}\n', "graph/nodes.jsonl": b"{}\n", "graph/edges.jsonl": b"{}\n",
             "index/bm25.json": b"{}", "raw/ley.html": b"<html>Ley</html>", "clean/ley.txt": b"Ley"}
    for rel, data in files.items():
        (corpus / rel).parent.mkdir(parents=True, exist_ok=True)
        (corpus / rel).write_bytes(data)
    manifest = {"hashes": {k: h(files[k]) for k in ("passages.jsonl", "graph/nodes.jsonl", "graph/edges.jsonl")},
                "bm25_sha256": h(files["index/bm25.json"]), "n_documentos": 1, "n_fragmentos": 1,
                "documentos": [{"raw_path": "corpus/raw/ley.html", "source_sha256": h(files["raw/ley.html"]),
                                "clean_path": "corpus/clean/ley.txt", "sha256": h(files["clean/ley.txt"])}]}
    (corpus / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return base


class PackageSnapshotTests(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(TMP, ignore_errors=True)
        self.repo = fixture_repo(TMP / "repo")

    def test_pack_is_deterministic_and_verifiable(self):
        a = pkg.pack(self.repo, TMP / "out_a")
        b = pkg.pack(self.repo, TMP / "out_b")
        self.assertEqual(a["archive_sha256"], b["archive_sha256"])
        self.assertEqual(a["files_verified"], 7)
        self.assertIn(a["archive_sha256"], (TMP / "out_a/LEEME.txt").read_text(encoding="utf-8"))
        self.assertEqual(pkg.verify(TMP / "out_a" / pkg.ARCHIVE_NAME, a["files"]), 7)
        with self.assertRaises(FileExistsError):
            pkg.pack(self.repo, TMP / "out_a")

    def test_refuses_modified_source_and_tampered_or_unsafe_archive(self):
        result = pkg.pack(self.repo, TMP / "good")
        tampered = dict(result["files"])
        tampered["corpus/passages.jsonl"] = "0" * 64
        with self.assertRaises(ValueError):
            pkg.verify(TMP / "good" / pkg.ARCHIVE_NAME, tampered)
        evil = TMP / "evil.tar.gz"
        with tarfile.open(evil, "w:gz") as tar:
            info = tarfile.TarInfo("../escape.txt")
            info.size = 1
            import io
            tar.addfile(info, io.BytesIO(b"x"))
        with self.assertRaises(ValueError):
            pkg.verify(evil, {"../escape.txt": h(b"x")})
        (self.repo / "corpus/passages.jsonl").write_bytes(b"cambiado")
        with self.assertRaises(ValueError):
            pkg.pack(self.repo, TMP / "bad")


if __name__ == "__main__":
    unittest.main()
