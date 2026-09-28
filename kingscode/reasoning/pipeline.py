"""A's public retrieve -> B router -> policy -> backend -> guards -> schema."""
from __future__ import annotations

from copy import deepcopy
from time import perf_counter

from .contracts import Question
from .decoder import GENERATION_CONFIG, Decoder, DummyDecoder, PromptSpec, abstention_row
from .guards import CitationGuardError, check_passages, citation_guard, validate_submission
from .policy import assess_evidence
from .query import normalize_query
from .routing import RetrieverGraphRouter, route_graph


def _answer(question: Question, passages: list[dict], decoder: Decoder):
    check_passages(passages)
    evidence = deepcopy(passages[:10])
    assessment = assess_evidence(question.text, evidence)
    if assessment.sufficient:
        row = decoder.generate(question, deepcopy(evidence), PromptSpec(question.format), dict(GENERATION_CONFIG))
        reason = "dummy_backend_no_legal_reasoning" if isinstance(decoder, DummyDecoder) else None
    else:
        reason = ",".join(assessment.reasons)
        if assessment.conflicts or "ineligible_evidence" in assessment.reasons:
            evidence = []
        row = abstention_row(question, evidence, reason)
    if not isinstance(row, dict) or row.get("id") != question.id or row.get("formato") != question.format:
        raise ValueError("Decoder changed question identity/format or did not return an object")
    guard = citation_guard(row, evidence)
    validate_submission(row)
    return row, {"assessment": assessment.record(), "abstention_reason": reason if row["abstencion"] else None,
                 "citation_guard": guard}


def answer(question: Question | str, passages: list[dict], format: str, *, question_id: int = 0, decoder: Decoder | None = None) -> dict:
    """Question carries the official ID; ad-hoc strings use question_id (default 0)."""
    q = Question(question_id, question, format) if isinstance(question, str) else question
    if not isinstance(q, Question) or q.format != format:
        raise TypeError("Use Question/plain text with a matching format; never a raw labeled row")
    return _answer(q, passages, decoder or DummyDecoder())[0]


class Pipeline:
    def __init__(self, retrieve, *, adapter: RetrieverGraphRouter | None = None, decoder: Decoder | None = None,
                 k: int = 8, graph_policy: str = "router"):
        if type(k) is not int or not 1 <= k <= 10 or graph_policy not in {"router", "off", "auto", "on"}:
            raise ValueError("Invalid evidence count/graph policy")
        self.retrieve, self.adapter = retrieve, adapter
        self.decoder, self.k, self.graph_policy = decoder or DummyDecoder(), k, graph_policy

    def run(self, question: Question):
        if not isinstance(question, Question):
            raise TypeError("Pipeline only accepts a public Question")
        start = perf_counter()
        query = normalize_query(question.text)
        flat = self.retrieve(query.retrieval_text, self.k, "off")
        check_passages(flat)
        decision = route_graph(query, flat) if self.graph_policy == "router" else self.graph_policy
        executed = "off"
        passages = flat
        if decision != "off":
            if self.adapter:
                self.adapter.bind(query.retrieval_text, decision)
            # Without a bound callback, call A explicitly with ON instead of
            # silently falling back to A's question-only provisional AUTO router.
            executed = decision if decision == "on" or self.adapter else "on"
            passages = self.retrieve(query.retrieval_text, self.k, executed)
        retrieved_ms = (perf_counter() - start) * 1000
        try:
            row, trace = _answer(question, passages, self.decoder)
        except CitationGuardError as exc:
            # Enunciado B.5: an unsupported/unsafe citation must be corrected or
            # suppressed, never void the whole run. _answer/answer() still raise
            # for direct callers (e.g. tamper-detection tests); only the batch
            # pipeline downgrades this single item to abstention so the other
            # 991 questions still publish. See docs/DECISION_LOG.md.
            evidence = deepcopy(passages[:10])
            row = abstention_row(question, evidence, "citation_guard_rejected")
            guard = citation_guard(row, evidence)
            trace = {"assessment": None, "abstention_reason": "citation_guard_rejected",
                     "citation_guard": guard, "citation_guard_fallback": exc.report}
        trace.update(id=question.id, query=query.record(), graph_decision=decision, graph_execution=executed,
                     flat_passage_ids=[p["passage_id"] for p in flat], final_passage_ids=[p["passage_id"] for p in passages],
                     latency_ms=(perf_counter() - start) * 1000, retrieval_ms=retrieved_ms)
        return row, trace
