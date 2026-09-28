"""Conservative evidence gate, without deciding substantive legal correctness."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
import re

from .legal import fold, supporting_passages
from .query import SIGNALS, NormalizedQuery, normalize_query

POLICY_VERSION = "evidence-policy-v1"
STOP = set("a al ante cual cuales como con de del el en es esta este la las lo los o para por que se si su un una y articulo articulos ley decreto codigo dice establece regula segun".split())


def terms(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z]+|\d+", fold(text)) if len(t) > 2 and t not in STOP}


def conflicts(passages: list[dict]) -> list[str]:
    found = set()
    for a, b in combinations(passages, 2):
        if a["passage_id"] == b["passage_id"] and a["text"] != b["text"]:
            found.add("same_passage_id_different_text")
        same_article = a["doc_id"] == b["doc_id"] and a.get("article") is not None and a.get("article") == b.get("article")
        if not same_article:
            continue
        if all(k in a and k in b for k in ("clean_start", "clean_end")) and (a["clean_start"], a["clean_end"]) == (b["clean_start"], b["clean_end"]) and a["text"] != b["text"]:
            found.add("same_source_interval_different_text")
        x, y = (fold(p["text"][len(p.get("text_prefix", "")):]).strip() for p in (a, b))
        denial = r"\bno\s+(?=podra\b|puede\b|debera\b|debe\b|procede\b|es\b)"
        if x != y and re.sub(denial, "", x) == re.sub(denial, "", y):
            found.add("opposed_literal_claims_same_article")
    return sorted(found)


@dataclass(frozen=True)
class EvidenceAssessment:
    sufficient: bool
    reasons: tuple[str, ...]
    conflicts: tuple[str, ...]
    lexical_overlap: int

    def record(self):
        return asdict(self)


def assess_evidence(question: str | NormalizedQuery, passages: list[dict]) -> EvidenceAssessment:
    q = question if isinstance(question, NormalizedQuery) else normalize_query(question)
    reasons = []
    if not q.normalized:
        reasons.append("empty_question")
    if not passages:
        reasons.append("retrieval_empty")
    if any(p.get("retrieval_eligible") is False or p.get("is_current_text") is False for p in passages):
        reasons.append("ineligible_evidence")
    conflict = conflicts(passages)
    if conflict:
        reasons.append("conflicting_evidence")
    exact = [r for r in q.references if r.complete]
    missing = [r for r in exact if not supporting_passages(r, passages)]
    if missing:
        reasons.append("missing_explicit_reference")
    if any(not r.complete for r in q.references):
        reasons.append("ambiguous_query_reference")
    if "temporality" in q.signals and not any(p.get("is_current_text") is True for p in passages):
        reasons.append("currency_not_certified")
    for signal in ("modification", "repeal", "referral", "regulation"):
        if signal in q.signals and not any(re.search(SIGNALS[signal], fold(p["text"])) for p in passages):
            reasons.append("missing_relation_evidence:" + signal)
    overlap = len(terms(q.normalized) & set().union(*(terms(p["text"]) for p in passages)))
    if passages and not exact and overlap < 2:
        reasons.append("weak_lexical_evidence")
    return EvidenceAssessment(not reasons, tuple(reasons), tuple(conflict), overlap)


# Reasons serious enough to abstain *before* even asking the decoder: no
# evidence at all, evidence that literally contradicts itself, or evidence
# tagged as not currently valid. Everything else (missing exact reference,
# ambiguous query, uncertified currency, weak lexical overlap...) is a soft
# signal: let the decoder try and rely on citation_guard's post-hoc check.
HARD_REASONS = frozenset({"empty_question", "retrieval_empty", "conflicting_evidence", "ineligible_evidence"})


def blocking_reasons(assessment: EvidenceAssessment, format: str) -> tuple[str, ...]:
    """Reasons that must abstain pre-decoder, given the official scoring rule.

    `multiple_choice` never blocks: per enunciado 6.1, guessing among the
    supplied options beats abstention even at random accuracy, so evidence
    quality alone is never a reason to withhold an attempt. Free-text formats
    still block on the reasons in HARD_REASONS.
    """
    if format == "multiple_choice":
        return ()
    return tuple(r for r in assessment.reasons if r in HARD_REASONS)
