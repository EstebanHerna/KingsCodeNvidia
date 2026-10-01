"""A's public retrieve -> B router -> policy -> backend -> guards -> schema."""
from __future__ import annotations

from copy import deepcopy
import inspect
from time import perf_counter

from .citation_builder import attach_references
from .citation_repair import count_citations, repair_citations
from .contracts import ANSWER_FIELDS, Question
from .decoder import GENERATION_CONFIG, Decoder, DummyDecoder, PromptSpec, abstention_row
from .guards import CitationGuardError, check_passages, citation_guard, validate_submission
from .policy import assess_evidence, blocking_reasons
from .query import NormalizedQuery, normalize_query
from .routing import RetrieverGraphRouter, route_graph


def query_variants(question: Question, query: NormalizedQuery) -> tuple[str, ...]:
    """One retrieval query per option for multiple_choice; the base query otherwise.

    Options carry terms the bare question omits (enunciado B.5's item 51: the
    action-type words needed to find Ley 472 de 1998 live in the options, not
    the question). Order is deterministic (sorted by letter) for reproducibility.
    """
    if question.format != "multiple_choice" or not question.options:
        return (query.retrieval_text,)
    return (query.retrieval_text,) + tuple(f"{query.retrieval_text} {v}" for _, v in sorted(question.options.items()))


def rrf_merge(ranked_lists: list[list[dict]], k: int, constant: int = 60) -> list[dict]:
    """Reciprocal rank fusion over A's own passage dicts; never mutates them."""
    scores: dict[str, float] = {}
    seen: dict[str, dict] = {}
    for ranked in ranked_lists:
        for rank, passage in enumerate(ranked):
            pid = passage["passage_id"]
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (constant + rank + 1)
            seen.setdefault(pid, passage)
    ordered = sorted(scores, key=lambda pid: (-scores[pid], pid))
    return [seen[pid] for pid in ordered[:k]]


RETRIEVAL_MODES = ("base", "option", "plan")
_LOCATOR_KWARGS = ("locator", "locator_injection", "exact_locator")


def locator_switch(retrieve) -> str | None:
    """Name of A's per-call exact-locator switch, if retrieve() exposes one."""
    try:
        params = inspect.signature(retrieve).parameters
    except (TypeError, ValueError):
        return None
    return next((name for name in _LOCATOR_KWARGS if name in params), None)


def supports_query_views(retrieve) -> bool:
    """A's retrieve(question, k, graph_mode, query_views=...) (v0.2): locator on question only."""
    try:
        return "query_views" in inspect.signature(retrieve).parameters
    except (TypeError, ValueError):
        return False


def retrieval_views(question: Question, query: NormalizedQuery, mode: str, plan=None) -> tuple[tuple[str, bool, str], ...]:
    """(text, trusted, role) per retrieval call. Q0 is always first and trusted.

    Options are organizer text (trusted). Planner views are model-generated:
    untrusted, so any statute/article they mention is plain retrieval text only.
    """
    q0 = (query.retrieval_text, True, "Q0")
    if mode == "base":
        return (q0,)
    if mode == "option":
        return (q0,) + tuple((v, True, "option") for v in query_variants(question, query)[1:])
    if mode == "plan":
        if plan is None:
            raise ValueError("plan mode needs a frozen plan (replay); plans are never generated inside the pipeline")
        return (q0,) + tuple((v, False, role) for v, role in zip(plan.views, plan.view_roles))
    raise ValueError(f"Unknown retrieval mode {mode}; plan+option is disabled until PLAN and OPTION are measured separately")


def _answer(question: Question, passages: list[dict], decoder: Decoder, *, max_refs: int = 3):
    check_passages(passages)
    evidence = deepcopy(passages[:10])
    assessment = assess_evidence(question.text, evidence)
    blocking = blocking_reasons(assessment, question.format)
    # Conflicting/ineligible text is never handed to the decoder or the guard,
    # whether or not it ends up blocking (e.g. it never blocks multiple_choice).
    if assessment.conflicts or "ineligible_evidence" in assessment.reasons:
        evidence = []
    # The official validator counts a non-abstaining row without pasajes_recuperados
    # as malformed (a failure, not even the 0.5), so no evidence => abstain, any format.
    if not evidence and not blocking:
        blocking = ("no_usable_evidence",)
    repair, refs, usage, before = None, [], {}, 0
    if blocking:
        reason, source = ",".join(blocking), "policy"
        row = abstention_row(question, evidence, reason)
    else:
        row = decoder.generate(question, deepcopy(evidence), PromptSpec(question.format), dict(GENERATION_CONFIG))
        usage = _usage(decoder)
        dummy = isinstance(decoder, DummyDecoder)
        reason = "dummy_backend_no_legal_reasoning" if dummy else None
        source = "dummy_backend" if dummy else "decoder"
        if isinstance(row, dict) and row.get("abstencion") is False and row.get("id") == question.id \
                and row.get("formato") == question.format:
            # Decoder reasons; citations are repaired against the evidence, then
            # final citation strings come from the deterministic builder (B2/B3).
            source, before = "none", count_citations(row)
            row, repair = repair_citations(row, evidence)
            row, refs = attach_references(row, evidence, usage.get("attribution"), max_refs)
            if question.format != "multiple_choice" and any(
                    row.get(k) in (None, "", [], {}) for k in ANSWER_FIELDS[question.format]):
                reason, source = "citation_repair_emptied_required_field", "citation_repair"
                row = abstention_row(question, evidence, reason)
    if not isinstance(row, dict) or row.get("id") != question.id or row.get("formato") != question.format:
        raise ValueError("Decoder changed question identity/format or did not return an object")
    guard = citation_guard(row, evidence)
    validate_submission(row)
    attribution = usage.get("attribution") or {"status": "legacy_fallback" if not blocking else "not_applicable", "ids": []}
    return row, {"assessment": assessment.record(), "warnings": [r for r in assessment.reasons if r not in blocking],
                 "abstention_reason": reason if row["abstencion"] else None, "abstention_source": source if row["abstencion"] else "none",
                 "citation_guard": guard, "citation_repair": repair, "built_references": refs,
                 "diagnostics": generation_diagnostics(decoder, usage, attribution, before, guard, repair, evidence, row)}


def _usage(decoder) -> dict:
    """Decoder-reported usage (HFDecoder.last_usage); anything that is not a dict is ignored."""
    usage = getattr(decoder, "last_usage", None)
    return dict(usage) if isinstance(usage, dict) else {}


def generation_diagnostics(decoder, usage, attribution, before, guard, repair, evidence, row) -> dict:
    """Label-free per-question generation diagnostics (no gold, no thresholds)."""
    actions = {}
    for action in (repair or {}).get("actions", []):
        actions[action["action"]] = actions.get(action["action"], 0) + 1
    return {"decoder": getattr(decoder, "name", type(decoder).__name__), "decoder_version": getattr(decoder, "version", None),
            "model": usage.get("model"), "revision": usage.get("revision"),
            "prompt_version": usage.get("prompt_version", PromptSpec(row["formato"]).version), "prompt_sha256": usage.get("prompt_sha256"),
            "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
            "generation_ms": usage.get("generation_ms"), "peak_vram_bytes": usage.get("peak_vram_bytes"),
            "peak_reserved_vram_bytes": usage.get("peak_reserved_vram_bytes"),
            "normalization_action": usage.get("normalization_action"), "decoder_abstained": usage.get("decoder_abstained"),
            "attribution_status": attribution.get("status"), "attribution_count": len(attribution.get("ids", [])),
            "attribution_reason": attribution.get("reason"), "format_warnings": list(usage.get("format_warnings") or []),
            "field_coercions": list(usage.get("field_coercions") or []), "evidence_in_prompt": usage.get("evidence_in_prompt"),
            "evidence_dropped_for_context": list(usage.get("evidence_dropped_for_context") or []),
            "citations_before_repair": before, "citations_after_repair": guard["citation_count"],
            "repair_actions": actions, "evidence_passages": len(evidence),
            "evidence_ids_delivered": [p.get("passage_id") for p in row["pasajes_recuperados"]],
            "evidence_ids_used": list(attribution.get("ids", []))}


def answer(question: Question | str, passages: list[dict], format: str, *, question_id: int = 0, decoder: Decoder | None = None) -> dict:
    """Question carries the official ID; ad-hoc strings use question_id (default 0)."""
    q = Question(question_id, question, format) if isinstance(question, str) else question
    if not isinstance(q, Question) or q.format != format:
        raise TypeError("Use Question/plain text with a matching format; never a raw labeled row")
    return _answer(q, passages, decoder or DummyDecoder())[0]


class Pipeline:
    def __init__(self, retrieve, *, adapter: RetrieverGraphRouter | None = None, decoder: Decoder | None = None,
                 k: int = 8, graph_policy: str = "router", retrieval_mode: str = "option", plans=None,
                 max_refs: int = 3):
        if type(k) is not int or not 1 <= k <= 10 or graph_policy not in {"router", "off", "auto", "on"}:
            raise ValueError("Invalid evidence count/graph policy")
        if retrieval_mode not in RETRIEVAL_MODES:
            raise ValueError(f"retrieval_mode must be one of {RETRIEVAL_MODES}; plan+option stays disabled until measured")
        if retrieval_mode == "plan" and plans is None:
            raise ValueError("plan mode replays frozen plans: pass plans=PlanStore(...)")
        self.retrieve, self.adapter = retrieve, adapter
        self.decoder, self.k, self.graph_policy = decoder or DummyDecoder(), k, graph_policy
        self.retrieval_mode, self.plans, self.max_refs = retrieval_mode, plans, max_refs
        self.locator_kwarg = locator_switch(retrieve)
        self.native_views = supports_query_views(retrieve)

    def _call(self, text: str, trusted: bool, mode: str) -> list[dict]:
        if not trusted and self.locator_kwarg:
            return self.retrieve(text, self.k, mode, **{self.locator_kwarg: False})
        return self.retrieve(text, self.k, mode)

    def _fetch(self, views, mode: str) -> list[dict]:
        # One view (the common case) keeps the exact call A/tests expect. Several
        # views (options or planner) fan out through A's public retrieve() and
        # are fused deterministically with RRF.
        if len(views) == 1:
            return self._call(views[0][0], views[0][1], mode)
        if self._native(views):
            # A's own multi-view path: the exact locator, graph router and
            # reranker see only Q0; generated views only widen candidates.
            return self.retrieve(views[0][0], self.k, mode, query_views=[text for text, _, _ in views[1:]])
        return rrf_merge([self._call(text, trusted, mode) for text, trusted, _ in views], self.k)

    def _native(self, views) -> bool:
        return self.native_views and views[0][1] and all(not trusted for _, trusted, _ in views[1:])

    def _locator_control(self, views) -> str | None:
        if all(trusted for _, trusted, _ in views):
            return None
        if self._native(views):
            return "a_query_views_locator_on_q0_only"
        return "disabled_for_generated_views" if self.locator_kwarg else "retrieve_has_no_locator_switch"

    def run(self, question: Question):
        if not isinstance(question, Question):
            raise TypeError("Pipeline only accepts a public Question")
        start = perf_counter()
        query = normalize_query(question.text)
        plan = self.plans.get(question.id, question.text) if self.retrieval_mode == "plan" else None
        variants = retrieval_views(question, query, self.retrieval_mode, plan)
        flat = self._fetch(variants, "off")
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
            passages = self._fetch(variants, executed)
        retrieved_ms = (perf_counter() - start) * 1000
        try:
            row, trace = _answer(question, passages, self.decoder, max_refs=self.max_refs)
        except CitationGuardError as exc:
            # Enunciado B.5: an unsupported/unsafe citation must be corrected or
            # suppressed, never void the whole run. _answer/answer() still raise
            # for direct callers (e.g. tamper-detection tests); only the batch
            # pipeline downgrades this single item to abstention so the other
            # 991 questions still publish. See docs/DECISION_LOG.md.
            evidence = deepcopy(passages[:10])
            row = abstention_row(question, evidence, "citation_guard_rejected")
            guard = citation_guard(row, evidence)
            usage = _usage(self.decoder)
            trace = {"assessment": None, "abstention_reason": "citation_guard_rejected", "abstention_source": "citation_guard_fallback",
                     "diagnostics": generation_diagnostics(self.decoder, usage, usage.get("attribution") or {"status": "legacy_fallback", "ids": []},
                                                           0, guard, None, evidence, row),
                     "citation_guard": guard, "citation_guard_fallback": exc.report}
        trace.update(retrieval_mode=self.retrieval_mode,
                     views=[{"role": role, "trusted": trusted, "text": text} for text, trusted, role in variants],
                     locator_control=self._locator_control(variants),
                     plan=None if plan is None else {"status": plan.status,
                                                     "generated_references": [list(map(str, r)) for r in plan.generated_references]})
        trace.update(id=question.id, query=query.record(), graph_decision=decision, graph_execution=executed,
                     flat_passage_ids=[p["passage_id"] for p in flat], final_passage_ids=[p["passage_id"] for p in passages],
                     latency_ms=(perf_counter() - start) * 1000, retrieval_ms=retrieved_ms)
        return row, trace
