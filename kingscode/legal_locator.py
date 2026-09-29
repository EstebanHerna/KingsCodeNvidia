"""Exact legal references and additive candidate injection; no evaluation inputs.

Identity comes from declared corpus metadata. A missed/ambiguous locator never
rewrites a number/year and never removes general retrieval candidates.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
import re

from .common import normalize
from .metadata import canonical_document_id, canonical_fragment_id

VERSION = "legal-locator-v1"
NORM = re.compile(r"\b(ley|decreto(?:\s+ley)?)\s+(?:no\.?\s*)?(\d+)\s*(?:de|/)\s*(\d{4})\b")
DECISION = re.compile(r"\b(su|sc|sl|sp|c|t)\s*[-–]?\s*(\d+)\s*(?:de|[-/])\s*(\d{4})\b")
ARTICLE_VALUE = r"\d+(?:[.,]\d+)*(?:\s*[-–]\s*\d+)?(?:\s*(?![ye]\s+\d)[a-z]\b)?"
ARTICLES = re.compile(r"\b(?:articulos?|arts?\.)\s+(" + ARTICLE_VALUE + r"(?:\s*(?:,\s+|\by\b|\be\b)\s*" + ARTICLE_VALUE + r")*)")
ALIASES = {
    "codigo general del proceso": "codigo_general_proceso", "cgp": "codigo_general_proceso",
    "codigo civil": "codigo_civil", "codigo de comercio": "codigo_comercio",
    "codigo comercio": "codigo_comercio", "codigo penal": "codigo_penal",
    "codigo sustantivo del trabajo": "codigo_sustantivo_trabajo", "cst": "codigo_sustantivo_trabajo",
    "estatuto tributario": "estatuto_tributario", "constitucion politica": "constitucion:1991",
    "constitucion de 1991": "constitucion:1991",
}


def article_key(value):
    return re.sub(r"\s+", "", normalize(str(value))).replace(",", ".").replace("–", "-")


def _norm_id(match):
    kind = "decreto" if match[1].startswith("decreto") else "ley"
    return f"{kind}:{int(match[2])}:{match[3]}"


def _decision_id(match):
    court = "corte_constitucional" if match[1] in {"c", "t", "su"} else "corte_suprema"
    return f"{court}:{match[1]}{int(match[2])}:{match[3]}"


@dataclass(frozen=True)
class LegalReference:
    document_id: str
    articles: tuple[str, ...] = ()
    subfragments: tuple[tuple[str, str], ...] = ()
    mention: str = ""


@dataclass(frozen=True)
class ParsedReferences:
    references: tuple[LegalReference, ...]
    unresolved: tuple[str, ...] = ()


def parse_references(question: str) -> ParsedReferences:
    if not isinstance(question, str):
        raise TypeError("Locator accepts only question text")
    text = normalize(question)
    mentions = [(m.start(), m.end(), _norm_id(m), m[0]) for m in NORM.finditer(text)]
    mentions += [(m.start(), m.end(), _decision_id(m), m[0]) for m in DECISION.finditer(text)]
    for alias, identity in ALIASES.items():
        mentions += [(m.start(), m.end(), identity, m[0]) for m in re.finditer(r"\b" + re.escape(alias) + r"\b", text)]
    mentions.sort()
    # Multiple textual forms of the same canonical work (e.g. CGP plus its
    # expanded title) are one identity, not competing attachment candidates.
    # Otherwise an explicitly stated article becomes ambiguous after alias
    # expansion and the locator broadens to every article in that work.
    unique_mentions = []
    seen_documents = set()
    for mention in mentions:
        if mention[2] in seen_documents:
            continue
        seen_documents.add(mention[2])
        unique_mentions.append(mention)
    mentions = unique_mentions
    groups = [[] for _ in mentions]
    subgroups = [[] for _ in mentions]
    unresolved = []

    def owner(start, end):
        if len(mentions) == 1:
            return 0
        # Prefer an explicit forward attachment: "art. 90 de la Ley ...".
        forward = [(i, m) for i, m in enumerate(mentions) if m[0] >= end
                   and re.fullmatch(r"\s*(?:de|del)(?:\s+la)?\s*", text[end:m[0]])]
        if len(forward) == 1:
            return forward[0][0]
        possible = []
        for i, (a, b, _, _) in enumerate(mentions):
            between = text[b:start] if b <= start else text[end:a] if end <= a else ""
            if re.search(r"[;?]|\b(?:versus|frente a)\b", between):
                continue
            possible.append((max(start-b, a-end, 0), i))
        possible.sort()
        if not possible or (len(possible)>1 and possible[0][0] == possible[1][0]):
            return None
        return possible[0][1]

    for match in ARTICLES.finditer(text):
        values = tuple(article_key(m[0]) for m in re.finditer(ARTICLE_VALUE, match[1]))
        idx = owner(match.start(), match.end())
        if idx is None:
            unresolved.append("article_without_unambiguous_document:" + match[1])
        else:
            groups[idx].extend(values)
    for match in re.finditer(r"\b(paragrafo|numeral|inciso)\s+(unico|primero|segundo|tercero|\d+)\b", text):
        idx = owner(match.start(), match.end())
        if idx is not None:
            value = {"primero": "1", "segundo": "2", "tercero": "3"}.get(match[2], match[2])
            subgroups[idx].append((match[1], value))
        else:
            unresolved.append("subfragment_without_unambiguous_document:" + match[0])
    if not mentions and re.search(r"\b(?:ley|decreto|sentencia|codigo)\b", text):
        unresolved.append("incomplete_or_unsupported_document_reference")
    refs = tuple(LegalReference(m[2], tuple(dict.fromkeys(groups[i])), tuple(dict.fromkeys(subgroups[i])), m[3])
                 for i, m in enumerate(mentions))
    return ParsedReferences(refs, tuple(unresolved))


class LegalLocator:
    def __init__(self, passages: list[dict]):
        self.passages = passages
        self.documents, self.fragments, self.identities = defaultdict(list), defaultdict(list), defaultdict(set)
        for i, p in enumerate(passages):
            doc = canonical_document_id(p)
            self.documents[doc].append(i)
            self.identities[doc].add(doc)
            if p.get("article") is not None:
                self.fragments[(doc, article_key(p["article"]))].append(i)
            # Code aliases and their exact enacting references are declared by
            # corpus titles, never inferred from a mention inside passage text.
            title = normalize(p.get("norm_name", ""))
            for m in NORM.finditer(title):
                self.identities[_norm_id(m)].add(doc)
            for m in DECISION.finditer(title):
                self.identities[_decision_id(m)].add(doc)
            for alias, identity in ALIASES.items():
                if re.search(r"\b" + re.escape(alias) + r"\b", title):
                    self.identities[identity].add(doc)
        for mapping in (self.documents, self.fragments):
            for values in mapping.values():
                values.sort(key=lambda i: passages[i]["passage_id"])

    def resolve_documents(self, reference: LegalReference) -> tuple[str, ...]:
        return tuple(sorted(self.identities.get(reference.document_id, ())))

    def resolve(self, question: str) -> dict:
        parsed = parse_references(question)
        hits, unresolved = defaultdict(list), list(parsed.unresolved)
        article_scoped = {doc for ref in parsed.references if ref.articles for doc in self.resolve_documents(ref)}
        for ref in parsed.references:
            docs = self.resolve_documents(ref)
            if not docs:
                unresolved.append("document_not_found:" + ref.document_id)
                continue
            for doc in docs:
                # B may append the expanded spelling of an alias. A repeated
                # document-only mention must not broaden an explicit article
                # request to every passage of that same document.
                if not ref.articles and doc in article_scoped:
                    continue
                indices = [i for a in ref.articles for i in self.fragments.get((doc, a), ())] if ref.articles else self.documents[doc]
                if not indices:
                    unresolved.append("fragment_not_found:" + doc + ":" + ",".join(ref.articles))
                for i in indices:
                    p = self.passages[i]
                    verified_sub = []
                    for kind, value in ref.subfragments:
                        field = {"paragrafo": "paragraph", "numeral": "clause", "inciso": "inciso"}[kind]
                        # Only explicit structured corpus metadata supports a
                        # subfragment hit; text mentions are not enough.
                        if p.get(field) is not None and article_key(p[field]) == value:
                            verified_sub.append([kind, value])
                    hits[i].append({"document_id": doc, "canonical_fragment_id": canonical_fragment_id(p),
                                    "articles": list(ref.articles), "verified_subfragments": verified_sub,
                                    "requested_subfragments": [list(x) for x in ref.subfragments]})
                if ref.subfragments and not any(len(h["verified_subfragments"]) == len(ref.subfragments)
                                                for i in indices for h in hits[i]):
                    unresolved.append("subfragment_unverified_article_or_document_candidates_retained:" + doc)
        return {"version": VERSION, "references": [asdict(r) for r in parsed.references],
                "indices": sorted(hits, key=lambda i: self.passages[i]["passage_id"]),
                "hits": dict(hits), "unresolved": sorted(set(unresolved))}


def candidate_union(general: list[int], locator: list[int]) -> list[int]:
    """Stable additive union. No hard filter, truncation, boost or gold lookup."""
    return list(dict.fromkeys([*general, *locator]))
