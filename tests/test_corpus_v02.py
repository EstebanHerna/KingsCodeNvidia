import unittest
from pathlib import Path

from kingscode.corpus import blocks_from_html
from kingscode.corpus_v02 import (
    join_split_article_headings, parse_document_v02, remove_decision_table_of_contents,
)
from kingscode.metadata import canonical_fragment_id
from kingscode.metadata import canonical_document_id

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures" / "corpus_v02"


def meta(doc_id, source_type, norm_name, number, year, canonical_body, url):
    return {
        "doc_id": doc_id, "source_type": source_type, "norm_name": norm_name,
        "norm_number": number, "year": year, "canonical_body": canonical_body,
        "source_url": url, "source_sha256": "fixture-source-sha256",
        "retrieved_at": "2026-09-29T00:00:00Z", "areas": ["Derecho constitucional"],
    }


class CorpusV02SourceRepairTests(unittest.TestCase):
    def test_d01_equal_content_hash_does_not_merge_distinct_documents(self):
        body = ["jurisprudencia", "C-1189", 2000]
        first = {"doc_id": "sentencia_c_1189_de_2000", "source_type": "decision",
                 "canonical_body": body, "source_url": "https://official.example/a",
                 "content_hash": "same-boilerplate-hash"}
        second = {"doc_id": "sentencia_c_127_de_2011", "source_type": "decision",
                  "canonical_body": ["jurisprudencia", "C-127", 2011],
                  "source_url": "https://official.example/b", "content_hash": "same-boilerplate-hash"}
        self.assertEqual(first["content_hash"], second["content_hash"])
        self.assertNotEqual(canonical_document_id(first), canonical_document_id(second))

    def test_fixtures_match_preserved_official_source_blocks(self):
        spans = __import__("json").loads((FIXTURES / "source_spans.json").read_text(encoding="utf-8-sig"))
        raw_root = ROOT.parent / "corpora" / "corpus-v0.2" / "raw"
        source_files = {
            "G02-SU214-TOC": ("sentencia_su_214_de_2016.html", "g02_su214_toc.txt", True),
            "C01-C355-REPEATED-HEADING": ("sentencia_c_355_de_2006.html", "c01_c355_sections.txt", True),
            "P02-LEY137-SPLIT-ARTICLE": ("ley_137_de_1994.html", "p02_ley137_articles.txt", False),
            "P01-LEY137-HEADING-BOUNDARY": ("ley_137_de_1994.html", "p01_ley137_heading_boundary.txt", False),
        }
        for fixture in spans["fixtures"]:
            filename, excerpt, decision = source_files[fixture["id"]]
            source_blocks, _ = blocks_from_html((raw_root / filename).read_bytes(), decision)
            expected = [source_blocks[i] for i in fixture["source_block_indices"]]
            actual = (FIXTURES / excerpt).read_text(encoding="utf-8-sig").splitlines()
            self.assertEqual(actual, expected, fixture["id"])

    def test_g02_removes_only_paginated_toc_rows(self):
        blocks = (FIXTURES / "g02_su214_toc.txt").read_text(encoding="utf-8-sig").splitlines()
        clean, excluded = remove_decision_table_of_contents(blocks)
        self.assertEqual(len(excluded), 1)
        self.assertNotIn("RESUELVE 201", clean)
        self.assertIn("ACLARACIÓN DE VOTO DEL MAGISTRADO", clean)
        self.assertIn("RESUELVE", clean)
        self.assertTrue(any(row.startswith("PRIMERO.") for row in clean))

    def test_c01_same_heading_occurrences_keep_distinct_fragment_ids(self):
        blocks = (FIXTURES / "c01_c355_sections.txt").read_text(encoding="utf-8-sig").splitlines()
        source = "<html><title>C-355</title><body><article><p>CONSIDERACIONES</p>" + "".join(f"<p>{b}</p>" for b in blocks) + "</article></body></html>"
        _, passages, _, _, info = parse_document_v02(
            meta("sentencia_c_355_de_2006", "decision", "Sentencia C-355 de 2006", "C-355", 2006,
                 ["jurisprudencia", "C-355", "2006"], "https://www.corteconstitucional.gov.co/relatoria/2006/c-355-06.htm"),
            source.encode("utf-8"),
        )
        matching = [p for p in passages if p["section"] == "Fundamentos lógicos"]
        self.assertEqual(len(matching), 3)
        ids = [canonical_fragment_id(p) for p in matching]
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual(len({p["source_unit_id"] for p in matching}), 3)

    def test_p02_joins_split_article_number_and_body(self):
        blocks = (FIXTURES / "p02_ley137_articles.txt").read_text(encoding="utf-8-sig").splitlines()
        joined = join_split_article_headings(blocks)
        self.assertEqual(len(joined), 2)
        self.assertTrue(str(joined[0]).startswith("Artículo 40 . Concepto favorable"))
        source = "<html><body><div class=\"descripcion-contenido\">" + "".join(f"<p>{b}</p>" for b in blocks) + "</div></body></html>"
        _, passages, _, _, _ = parse_document_v02(
            meta("ley_137_de_1994", "law", "Ley 137 de 1994", "137", 1994,
                 ["ley", "137", "1994"], "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=13966"),
            source.encode("utf-8"),
        )
        self.assertEqual([p["article"] for p in passages], ["40", "41"])

    def test_p01_major_heading_closes_prior_article(self):
        blocks = (FIXTURES / "p01_ley137_heading_boundary.txt").read_text(encoding="utf-8-sig").splitlines()
        source = "<html><body><div class=\"descripcion-contenido\">" + "".join(f"<p>{b}</p>" for b in blocks) + "</div></body></html>"
        _, passages, _, _, _ = parse_document_v02(
            meta("ley_137_de_1994", "law", "Ley 137 de 1994", "137", 1994,
                 ["ley", "137", "1994"], "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=13966"),
            source.encode("utf-8"),
        )
        article45 = next(p for p in passages if p["article"] == "45")
        article46 = next(p for p in passages if p["article"] == "46")
        self.assertNotIn("CAPITULO IV", article45["text"])
        self.assertNotIn("Del Estado de Emergencia", article45["text"])
        self.assertIn("CAPITULO IV", article46["hierarchy_path"])


if __name__ == "__main__":
    unittest.main()
