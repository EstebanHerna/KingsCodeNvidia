"""Tests for the v0.6 canonical identity, metadata, dedup and failure taxonomy.

Mechanical unit tests only. No sample answers, no legal_basis, no training data.
Fixtures are hand-built minimal records, never competitive data.
"""
from __future__ import annotations

import unittest

from kingscode.acquisition_backlog import classify_target
from kingscode.diversify import (
    collapse_duplicates,
    dedup_key,
    diversify,
    group_duplicates,
    locator_boost,
    metadata_features,
    parse_reference,
)
from kingscode.metadata import (
    canonical_document_id,
    canonical_fragment_id,
    content_hash,
    document_metadata,
    embedding_representation,
    enrich_passage,
    passage_metadata,
    temporal_status,
)


def _passage(**over):
    base = {"passage_id": "codigo_civil:00042:abc", "doc_id": "codigo_civil",
            "source_type": "code", "canonical_body": ["codigo_civil", None, None],
            "norm_name": "Código Civil", "norm_number": None, "year": None,
            "article": "1602", "paragraph": None, "clause": None, "section": None,
            "hierarchy_path": ["Código Civil"], "order_index": 42,
            "graph_node_ids": ["doc:codigo_civil"], "retrieval_eligible": True,
            "text_prefix": "Código Civil.\n", "text": "Código Civil.\nTodo contrato es ley.",
            "is_current_text": None, "source_url": "https://example.test/cc",
            "source_sha256": "a" * 64, "retrieved_at": "2026-09-28T00:00:00Z"}
    base.update(over)
    return base


class CanonicalDocumentIdTests(unittest.TestCase):
    def test_law(self):
        p = _passage(canonical_body=["ley", "1564", "2012"], source_type="code",
                     doc_id="codigo_general_proceso")
        # A law body still resolves to its ley:number:year identity.
        self.assertEqual(canonical_document_id(p), "ley:1564:2012")

    def test_decree(self):
        p = _passage(canonical_body=["decreto", "410", "1971"], source_type="code",
                     doc_id="codigo_comercio")
        self.assertEqual(canonical_document_id(p), "decreto:410:1971")

    def test_named_code_alias(self):
        p = _passage(canonical_body=["codigo_civil", None, None], doc_id="codigo_civil")
        self.assertEqual(canonical_document_id(p), "codigo_civil")

    def test_constitution(self):
        p = _passage(canonical_body=["constitucion", None, None], doc_id="constitucion",
                     source_type="constitution", year=1991)
        self.assertEqual(canonical_document_id(p), "constitucion:1991")

    def test_constitutional_judgment(self):
        p = _passage(canonical_body=["jurisprudencia", "C-355", "2006"], source_type="decision",
                     doc_id="sentencia_c_355_de_2006", article=None, section="CONSIDERACIONES")
        self.assertEqual(canonical_document_id(p), "corte_constitucional:c355:2006")

    def test_supreme_court_judgment(self):
        p = _passage(canonical_body=["jurisprudencia", "SL-3385", "2022"], source_type="decision",
                     doc_id="sentencia_sl_3385_de_2022", article=None)
        self.assertEqual(canonical_document_id(p), "corte_suprema:sl3385:2022")

    def test_url_independence(self):
        a = _passage(canonical_body=["ley", "1564", "2012"], source_url="https://a.gov/x")
        b = _passage(canonical_body=["ley", "1564", "2012"], source_url="https://mirror.gov/y")
        self.assertEqual(canonical_document_id(a), canonical_document_id(b))


class CanonicalFragmentIdTests(unittest.TestCase):
    def test_law_article(self):
        p = _passage(canonical_body=["ley", "1564", "2012"], article="391", doc_id="cgp")
        self.assertEqual(canonical_fragment_id(p), "ley:1564:2012:articulo:391")

    def test_code_article(self):
        p = _passage(article="1602")
        self.assertEqual(canonical_fragment_id(p), "codigo_civil:articulo:1602")

    def test_document_and_fragment_ids_are_separate(self):
        p = _passage(article="1602")
        self.assertNotEqual(canonical_document_id(p), canonical_fragment_id(p))
        self.assertTrue(canonical_fragment_id(p).startswith(canonical_document_id(p) + ":"))

    def test_historical_variant_stays_distinct(self):
        current = _passage(article="14", is_current_text=None)
        historical = _passage(article="14", is_current_text=False)
        self.assertNotEqual(canonical_fragment_id(current), canonical_fragment_id(historical))
        self.assertTrue(canonical_fragment_id(historical).endswith(":historico"))

    def test_duplicate_article_headings_stay_distinct(self):
        a = _passage(article="1", duplicate_article_heading=True, order_index=10)
        b = _passage(article="1", duplicate_article_heading=True, order_index=20)
        self.assertNotEqual(canonical_fragment_id(a), canonical_fragment_id(b))

    def test_judgment_section_fragment(self):
        p = _passage(canonical_body=["jurisprudencia", "C-355", "2006"], source_type="decision",
                     doc_id="scc", article=None, section="DECISION")
        self.assertTrue(canonical_fragment_id(p).startswith("corte_constitucional:c355:2006:seccion:"))


class ContentHashTests(unittest.TestCase):
    def test_excludes_prefix_and_mirrors_collapse(self):
        a = _passage(text_prefix="Código Civil.\n", text="Código Civil.\nTexto igual.")
        b = _passage(text_prefix="CC (espejo oficial).\n", text="CC (espejo oficial).\nTexto igual.")
        # Same body text through two mirrors -> same content hash.
        self.assertEqual(content_hash(a), content_hash(b))

    def test_distinct_bodies_differ(self):
        a = _passage(text="Código Civil.\nUno.")
        b = _passage(text="Código Civil.\nDos.")
        self.assertNotEqual(content_hash(a), content_hash(b))


class TemporalTests(unittest.TestCase):
    def test_unknown_by_default(self):
        self.assertEqual(temporal_status(_passage())["status_assertion"], "unknown")

    def test_historical_with_evidence(self):
        t = temporal_status(_passage(is_current_text=False, passage_id="pid-1"))
        self.assertEqual(t["status_assertion"], "historical")
        self.assertEqual(t["status_source_passage_id"], "pid-1")

    def test_no_invented_effective_dates(self):
        t = temporal_status(_passage())
        self.assertIsNone(t["effective_from"])
        self.assertIsNone(t["effective_to"])


class MetadataViewTests(unittest.TestCase):
    def test_passage_metadata_carries_content_hash_not_text(self):
        m = passage_metadata(_passage())
        self.assertIn("content_hash", m)
        self.assertNotIn("text", m)
        self.assertNotIn("source_url", m)

    def test_document_metadata_separates_provenance(self):
        m = document_metadata(_passage(canonical_body=["ley", "1564", "2012"]))
        self.assertEqual(m["canonical_document_id"], "ley:1564:2012")
        self.assertIn("source_sha256", m)
        self.assertEqual(m["status_assertion"], "unknown")

    def test_enrich_is_additive_and_keeps_text(self):
        p = _passage()
        e = enrich_passage(p)
        self.assertEqual(e["text"], p["text"])
        self.assertEqual(e["canonical_fragment_id"], canonical_fragment_id(p))
        self.assertEqual(e["metadata_version"], "metadata-v0.6")


class BacklogClassifierTests(unittest.TestCase):
    def _t(self, **over):
        base = {"doc_id": "x", "canonical_body": ["ley", "80", "1993"],
                "norm_name": "Ley 80 de 1993", "source_type": "law", "areas": [],
                "error": "No exact document found in official catalogue"}
        base.update(over)
        return base

    def test_supreme_court_is_source_unavailable(self):
        r = classify_target(self._t(canonical_body=["jurisprudencia", "SL-648", "2018"],
                                    source_type="decision", error="Needs verified Corte Suprema/Consejo de Estado URL"),
                            resolved_ids=set())
        self.assertEqual(r["resolution"], "source_unavailable")

    def test_out_of_range_law_is_identifier_suspect(self):
        r = classify_target(self._t(canonical_body=["ley", "11500", "2007"]), resolved_ids=set())
        self.assertEqual(r["resolution"], "identifier_suspect")

    def test_plausible_missing_law_is_not_found(self):
        r = classify_target(self._t(canonical_body=["ley", "964", "2006"]), resolved_ids=set())
        self.assertEqual(r["resolution"], "not_found")

    def test_named_instrument_is_ambiguous(self):
        r = classify_target(self._t(canonical_body=["acuerdo", "02", "2015"], source_type="code",
                                    error="Needs manually verified official URL for named code/instrument"),
                            resolved_ids=set())
        self.assertEqual(r["resolution"], "ambiguous")

    def test_resolved_when_present(self):
        r = classify_target(self._t(doc_id="ley_80_de_1993"), resolved_ids={"ley_80_de_1993"})
        self.assertEqual(r["resolution"], "resolved")

    def test_never_rewrites_identifier(self):
        t = self._t(canonical_body=["ley", "11500", "2007"])
        r = classify_target(t, resolved_ids=set())
        self.assertEqual(r["canonical_body"], ["ley", "11500", "2007"])


class DedupDiversifyTests(unittest.TestCase):
    def test_mirror_collapse_preserves_provenance(self):
        a = _passage(passage_id="p1", source_url="https://a.gov/x",
                     text_prefix="A.\n", text="A.\nCuerpo idéntico.")
        b = _passage(passage_id="p2", source_url="https://mirror.gov/y",
                     text_prefix="B (espejo).\n", text="B (espejo).\nCuerpo idéntico.")
        out = collapse_duplicates([a, b], level="content")
        self.assertEqual(len(out), 1)
        members = out[0]["duplicate_group"]["members"]
        self.assertEqual({m["passage_id"] for m in members}, {"p1", "p2"})
        self.assertEqual({m["source_url"] for m in members}, {"https://a.gov/x", "https://mirror.gov/y"})

    def test_group_by_levels(self):
        p = _passage()
        self.assertEqual(dedup_key(p, "document"), canonical_document_id(p))
        self.assertEqual(dedup_key(p, "fragment"), canonical_fragment_id(p))
        self.assertEqual(dedup_key(p, "content"), content_hash(p))
        with self.assertRaises(ValueError):
            dedup_key(p, "bogus")
        self.assertEqual(len(group_duplicates([p, p], "content")), 1)

    def test_diversify_caps_per_group_without_loss(self):
        docs = [_passage(passage_id=f"cc{i}", article=str(i), order_index=i) for i in range(4)]
        others = [_passage(passage_id="ley1", canonical_body=["ley", "1564", "2012"],
                           doc_id="cgp", article="10", order_index=99)]
        ranked = docs + others
        out = diversify(ranked, k=5, level="document", max_per_group=2)
        # All five kept (nothing lost) but the first two are capped per document.
        self.assertEqual(len(out), 5)
        self.assertEqual(out[2]["passage_id"], "ley1")

    def test_diversify_bad_arg(self):
        with self.assertRaises(ValueError):
            diversify([_passage()], k=1, max_per_group=0)


class ReferenceFeatureTests(unittest.TestCase):
    def test_parse_law_article_decision_code(self):
        ref = parse_reference("Según la Ley 1564 de 2012 artículo 391 y la Sentencia C-355 de 2006 del Código Civil")
        self.assertEqual(ref["norms"], [{"kind": "ley", "number": "1564", "year": "2012"}])
        self.assertIn("391", ref["articles"])
        self.assertEqual(ref["decisions"][0]["year"], "2006")
        self.assertTrue(ref["has_explicit_reference"])

    def test_exact_norm_and_article_match(self):
        p = _passage(canonical_body=["ley", "1564", "2012"], source_type="law", article="391", doc_id="cgp")
        feats = metadata_features("Ley 1564 de 2012 artículo 391", p)
        self.assertTrue(feats["exact_norm_match"])
        self.assertTrue(feats["exact_article_match"])
        self.assertTrue(feats["same_document"])

    def test_features_never_none_filter(self):
        p = _passage(article="999")
        feats = metadata_features("Ley 1564 de 2012 artículo 391", p)
        self.assertFalse(feats["exact_article_match"])
        # temporal_match true by default (not historical)
        self.assertTrue(feats["temporal_match"])

    def test_locator_boost_is_bounded_and_deterministic(self):
        feats = {"exact_norm_match": True, "exact_article_match": True,
                 "source_type_match": True, "temporal_match": True}
        self.assertEqual(locator_boost(feats), 1.0)
        self.assertEqual(locator_boost({}), 0.0)


class FailureTaxonomyTests(unittest.TestCase):
    def _pred(self, **over):
        base = {"id": 1, "area": "Derecho civil", "format": "open", "graph_mode": "off",
                "graph_active": False, "coverage": 1.0,
                "retrieved_targets": [["ley", "1564", "2012", "391"]],
                "metrics": {"evaluable": True, "legal_basis_any@10": True, "document_mismatch@1": False}}
        base.update(over)
        return base

    def _audit(self, **over):
        base = {"id": 1, "targets": [["ley", "1564", "2012", "391"]],
                "covered_targets": [["ley", "1564", "2012", "391"]], "coverage": 1.0, "notes": []}
        base.update(over)
        return base

    def test_success_wins_over_noisy_label(self):
        from kingscode.failure_analysis import classify_question
        r = classify_question(self._pred(), self._audit(notes=["Document-level label only"]))
        self.assertEqual(r["class"], "success")

    def test_corpus_missing(self):
        from kingscode.failure_analysis import classify_question
        pred = self._pred(coverage=0.0, retrieved_targets=[["ley", "9", "9", "9"]],
                          metrics={"evaluable": True, "legal_basis_any@10": False, "document_mismatch@1": True})
        r = classify_question(pred, self._audit(coverage=0.0, covered_targets=[]))
        self.assertEqual(r["class"], "corpus_missing")

    def test_correct_document_wrong_passage(self):
        from kingscode.failure_analysis import classify_question
        pred = self._pred(retrieved_targets=[["ley", "1564", "2012", "999"]],
                          metrics={"evaluable": True, "legal_basis_any@10": False, "document_mismatch@1": False})
        r = classify_question(pred, self._audit())
        self.assertEqual(r["class"], "correct_document_wrong_passage")

    def test_wrong_document(self):
        from kingscode.failure_analysis import classify_question
        pred = self._pred(retrieved_targets=[["ley", "80", "1993", "1"]],
                          metrics={"evaluable": True, "legal_basis_any@10": False, "document_mismatch@1": True})
        r = classify_question(pred, self._audit())
        self.assertEqual(r["class"], "wrong_document")

    def test_ambiguous_document_only_label_on_failure(self):
        from kingscode.failure_analysis import classify_question
        pred = self._pred(retrieved_targets=[["ley", "80", "1993", None]],
                          metrics={"evaluable": True, "legal_basis_any@10": False, "document_mismatch@1": True})
        audit = self._audit(targets=[["ley", "1564", "2012", None]], covered_targets=[])
        r = classify_question(pred, audit)
        self.assertEqual(r["class"], "ambiguous_ground_truth")

    def test_graph_failure_signal(self):
        from kingscode.failure_analysis import classify_question
        pred = self._pred(retrieved_targets=[["ley", "80", "1993", "1"]], graph_active=False,
                          metrics={"evaluable": True, "legal_basis_any@10": False, "document_mismatch@1": True})
        r = classify_question(pred, self._audit(), "¿Qué artículo modifica y deroga el parágrafo?")
        self.assertEqual(r["class"], "graph_failure")


class EmbeddingRepresentationTests(unittest.TestCase):
    def test_header_has_norm_article_no_provenance(self):
        p = _passage(canonical_body=["ley", "1564", "2012"], norm_name="Código General del Proceso",
                     article="391", hierarchy_path=["Código General del Proceso", "LIBRO PRIMERO"],
                     text_prefix="CGP.\n", text="CGP.\nEl proceso verbal sumario...")
        rep = embedding_representation(p)
        self.assertIn("Ley 1564 de 2012", rep)
        self.assertIn("Artículo 391", rep)
        self.assertIn("LIBRO PRIMERO", rep)
        self.assertIn("El proceso verbal sumario", rep)
        for banned in ["sha256", "http", "retrieved_at", "raw_path", ".jsonl", "a" * 64]:
            self.assertNotIn(banned, rep.lower())

    def test_decision_representation(self):
        p = _passage(canonical_body=["jurisprudencia", "C-355", "2006"], source_type="decision",
                     decision_id="C-355", norm_name="Sentencia C-355 de 2006", article=None,
                     year=2006, text_prefix="S.\n", text="S.\nLa Corte considera...")
        rep = embedding_representation(p)
        self.assertIn("Sentencia C-355 de 2006", rep)
        self.assertIn("La Corte considera", rep)


class GraphTemporalAuditTests(unittest.TestCase):
    def test_temporal_states_present_and_evidence_defect_counted(self):
        from kingscode.coverage_report import graph_temporal_audit
        passages = [_passage(is_current_text=None), _passage(is_current_text=False)]
        nodes = [{"node_id": "doc:x", "node_type": "NORM"}]
        edges = [{"source": "a", "target": "b", "relation": "CITA",
                  "evidence_passage_id": "p1", "evidence_text": "x", "method": "explicit_text_reference"},
                 {"source": "a", "target": "b", "relation": "MODIFICA",
                  "evidence_passage_id": "", "evidence_text": "", "method": None}]
        audit = graph_temporal_audit(passages, nodes, edges)
        for s in ["current", "historical", "repealed", "modified", "unknown"]:
            self.assertIn(s, audit["temporal_status_distribution"])
        self.assertEqual(audit["temporal_status_distribution"]["historical"], 1)
        self.assertEqual(audit["temporal_status_distribution"]["unknown"], 1)
        self.assertEqual(audit["edges_without_evidence"], 1)
        self.assertEqual(audit["normative_edges_without_provenance"], 1)


if __name__ == "__main__":
    unittest.main()
