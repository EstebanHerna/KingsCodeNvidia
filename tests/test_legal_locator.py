"""Mechanical fixtures, independent of any benchmark gold or legal answers."""
from collections import defaultdict
from unittest.mock import Mock, patch
import unittest

from kingscode.legal_locator import LegalLocator, parse_references, candidate_union
from kingscode.metadata import canonical_document_id
from kingscode.retrieval import Retriever


def passage(pid, body, article=None, name=None, **kw):
    return {"passage_id": pid, "doc_id": pid.split(":")[0], "canonical_body": body,
            "norm_name": name or f"Ley {body[1]} de {body[2]}", "article": article,
            "text": "mechanical fixture " + pid, "graph_node_ids": [],
            "source_url": "https://example.test/fixture", **kw}


class LocatorTests(unittest.TestCase):
    def setUp(self):
        self.ps = [passage("law:90", ["ley", "1564", "2012"], "90"),
                   passage("law:91", ["ley", "1564", "2012"], "91"),
                   passage("other:1", ["ley", "1", "2000"], "1"),
                   passage("other:2a", ["ley", "1", "2000"], "2A"),
                   passage("dec:1", ["decreto", "1072", "2015"], "2.2.1.1"),
                   passage("case:1", ["jurisprudencia", "C-355", "2006"], name="Sentencia C-355 de 2006", source_type="decision"),
                   passage("supreme:1", ["jurisprudencia", "SL-648", "2018"], name="Sentencia SL648-2018", source_type="decision")]
        self.loc = LegalLocator(self.ps)

    def hits(self, text): return self.loc.resolve(text)["indices"]

    def test_exact_law_year_article(self):
        self.assertEqual(self.hits("Ley 1564 de 2012, artículo 90"), [0])

    def test_alias_resolves_declared_code_enacting_identity(self):
        p = passage("codigo_general_proceso:90", ["code", None, None], "90", "Código General del Proceso (Ley 1564 de 2012)", source_type="code")
        loc = LegalLocator([p])
        for q in ("CGP art. 90", "Código General del Proceso artículo 90", "Ley 1564 de 2012 art. 90"):
            result = loc.resolve(q)
            self.assertEqual(result["indices"], [0])
            self.assertEqual(result["hits"][0][0]["document_id"], canonical_document_id(p))

    def test_multiple_articles_and_suffixes(self):
        self.assertEqual(self.hits("Ley 1564 de 2012 arts. 90 y 91"), [0, 1])
        self.assertEqual(self.hits("Ley 1564 de 2012 artículos 90, 91"), [0, 1])
        self.assertEqual(self.hits("Ley 1 de 2000 artículo 2 A"), [3])
        self.assertEqual(self.hits("Decreto 1072 de 2015 artículo 2.2.1.1"), [4])

    def test_decisions(self):
        self.assertEqual(self.hits("Sentencia C-355 de 2006"), [5])
        self.assertEqual(self.hits("SL648-2018"), [6])
        for letter in ("T", "SU", "SC", "SP"):
            parsed = parse_references(f"Sentencia {letter}-123 de 2020")
            self.assertEqual(len(parsed.references), 1)

    def test_no_explicit_reference(self):
        self.assertEqual(self.hits("Una consulta conceptual sin citas"), [])

    def test_no_approximate_substitution(self):
        for q in ("Ley 1564 de 2013 artículo 90", "Ley 1565 de 2012 artículo 90", "Ley 1564 de 2012 artículo 900"):
            self.assertEqual(self.hits(q), [])
            self.assertTrue(self.loc.resolve(q)["unresolved"])

    def test_ambiguous_number(self):
        self.assertEqual(self.hits("artículo 90"), [])
        self.assertEqual(self.hits("Ley 1564 artículo 90"), [])

    def test_multiple_norms_associate_articles(self):
        q = "art. 90 de la Ley 1564 de 2012 y art. 1 de la Ley 1 de 2000"
        self.assertEqual(self.hits(q), [0, 2])
        refs = parse_references(q).references
        self.assertEqual([r.articles for r in refs], [("90",), ("1",)])

    def test_subfragment_fallback_is_explicit(self):
        result = self.loc.resolve("Ley 1564 de 2012 artículo 90 parágrafo 1 inciso segundo")
        self.assertEqual(result["indices"], [0])
        self.assertEqual(result["hits"][0][0]["verified_subfragments"], [])
        self.assertTrue(any("subfragment_unverified" in s for s in result["unresolved"]))

    def test_structured_subfragment(self):
        self.ps[0]["paragraph"] = "1"
        result = self.loc.resolve("Ley 1564 de 2012 artículo 90 parágrafo 1")
        self.assertEqual(result["hits"][0][0]["verified_subfragments"], [["paragrafo", "1"]])

    def test_union_preserves_all_general_candidates_and_order(self):
        self.assertEqual(candidate_union([8, 2, 5], [2, 1]), [8, 2, 5, 1])

    def test_determinism_and_no_gold_input(self):
        text = "Ley 1564 de 2012 arts. 90 y 91"
        self.assertEqual(self.loc.resolve(text), LegalLocator(self.ps).resolve(text))
        with self.assertRaises(TypeError): self.loc.resolve({"question": text, "gold": [0]})

    def test_reference_mentions_in_body_do_not_create_identity(self):
        self.ps[2]["text"] = "Ley 1564 de 2012 artículo 90"
        self.assertEqual(LegalLocator(self.ps).resolve("Ley 1564 de 2012 art. 90")["indices"], [0])

    def test_b_normalization_contract(self):
        from kingscode.reasoning.query import normalize_query
        value = normalize_query("  Ley 1564 de 2012, artículo 90  ")
        self.assertEqual(self.hits(value.normalized), [0])

    def test_b_alias_expansion_does_not_broaden_explicit_article(self):
        from kingscode.reasoning.query import normalize_query
        ps=[passage(f"codigo_general_proceso:{a}",["code",None,None],str(a),
                    "Código General del Proceso (Ley 1564 de 2012)",source_type="code") for a in (90,91)]
        loc=LegalLocator(ps)
        value=normalize_query("CGP art. 90")
        self.assertEqual(loc.resolve(value.retrieval_text)['indices'],[0])
        self.assertEqual(loc.resolve("CGP artículo 90. Código General del Proceso")['indices'],[0])

    def test_retriever_injects_before_reranker_without_filtering(self):
        retriever = Retriever.__new__(Retriever)
        retriever.passages = self.ps
        retriever.corpus_hash = "fixture"
        retriever.mode, retriever.candidate_k, retriever.graph_budget = "bm25", 1, 0
        retriever.legal_locator, retriever.dense = self.loc, None
        retriever.router = lambda _: False
        retriever.bm25 = Mock()
        retriever.bm25.ranking.return_value = ([2], {2: 3.0})
        retriever.reranker = Mock()
        retriever.reranker.score.return_value = [0.1, 0.9]  # general then locator
        out = retriever.retrieve("Ley 1564 de 2012 art. 90", 1, "off")
        self.assertEqual(retriever.reranker.score.call_args.args[1], [self.ps[2]["text"], self.ps[0]["text"]])
        self.assertEqual(out[0]["passage_id"], "law:90")
        self.assertTrue(out[0]["locator"]["hit"])
        self.assertEqual(out[0]["source_url"], self.ps[0]["source_url"])
        self.assertEqual(out[0]["retrieval"]["union_candidate_count"], 2)

    def test_public_profile_and_legacy_opt_out(self):
        from kingscode import retrieval
        retrieval._default_retriever.cache_clear()
        with patch.object(retrieval, "Retriever") as ctor:
            retrieval._default_retriever("fixture")
            self.assertTrue(ctor.call_args.kwargs['exact_locator'])
            self.assertFalse(ctor.call_args.kwargs['graph_router']('modificacion o derogacion'))
            self.assertNotIn('graph_budget',ctor.call_args.kwargs)  # explicit ON retains its historical budget
        retrieval._default_retriever.cache_clear()
        import inspect
        self.assertFalse(inspect.signature(Retriever).parameters["exact_locator"].default)


if __name__ == "__main__": unittest.main()
