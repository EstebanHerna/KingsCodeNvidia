"""Reversible text cleanup and finite, auditable legal alias expansion."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
import unicodedata

from .legal import CODE_ALIASES, Reference, fold, references

QUERY_VERSION = "legal-query-v1"
SIGNALS = {
    "modification": r"\b(?:modific\w*|reform\w*|adicion\w*|sustitu\w*)\b",
    "repeal": r"\b(?:derog\w*|inexequib\w*)\b",
    "referral": r"\b(?:remis\w*|remit\w*|concordancia\w*)\b",
    "regulation": r"\b(?:reglament\w*|desarrolla\w*)\b",
    "hierarchy": r"\b(?:jerarquia|prevalec\w*|paragrafo\w*|inciso\w*|numeral\w*|subsidiari\w*)\b",
    "temporality": r"\b(?:vigencia|vigente\w*|actualmente|hoy|retroactiv\w*|ultractiv\w*|transitori\w*)\b|\ba partir de\b|\bantes de\b|\bdespues de\b",
}
AUTHORITIES = ("Corte Constitucional", "Corte Suprema de Justicia", "Consejo de Estado", "Congreso de la República",
               "DIAN", "Superintendencia de Industria y Comercio", "Procuraduría General de la Nación", "Fiscalía General de la Nación")


@dataclass(frozen=True)
class NormalizedQuery:
    original: str
    normalized: str
    retrieval_text: str
    references: tuple[Reference, ...]
    authorities: tuple[str, ...]
    signals: tuple[str, ...]
    expansions: tuple[str, ...]
    version: str = QUERY_VERSION

    def record(self):
        return asdict(self)


def normalize_query(question: str) -> NormalizedQuery:
    if not isinstance(question, str):
        raise TypeError("Only question text is accepted; pass no sample/label records")
    text = re.sub(r"\s+", " ", unicodedata.normalize("NFC", question)).strip()
    refs = references(text)
    expansions = []
    for ref in refs:
        if ref.kind == "code":
            full = CODE_ALIASES[ref.body[0]][0]
            if fold(full) not in fold(text) and full not in expansions:
                expansions.append(full)
    # Add at most four exact alias expansions; never replace the user's wording,
    # punctuation, reference digits, negations, or temporal constraints.
    expansions = expansions[:4]
    retrieval = text + ("\n" + " ; ".join(expansions) if expansions else "")
    folded = fold(text)
    return NormalizedQuery(question, text, retrieval, tuple(refs),
                           tuple(a for a in AUTHORITIES if re.search(r"\b" + re.escape(fold(a)) + r"\b", folded)),
                           tuple(k for k, pattern in SIGNALS.items() if re.search(pattern, folded)), tuple(expansions))
