"""Deterministic classification of unresolved acquisition targets (Phase 1, v0.6).

This module NEVER downloads a substitute norm, NEVER edits a seed identifier and
NEVER guesses a canonical URL. It reads the acquisition report produced by the
Corpus v0.1 build and assigns every failed target to one auditable resolution
class, preserving provenance and a human-readable note.

Resolution classes
-------------------
- ``resolved``            the target is present in the parsed corpus after review.
- ``not_found``           an official-catalogue search ran but returned no exact
                          number/year match; identity is plausible.
- ``source_unavailable``  the issuing body / catalogue is not reachable through
                          the current official resolver (e.g. Corte Suprema and
                          Consejo de Estado have no verified URL builder yet).
- ``ambiguous``           a named instrument or reference whose canonical target
                          cannot be pinned down deterministically without a
                          manually verified official URL.
- ``identifier_suspect``  the seed identifier itself is structurally implausible
                          for the declared issuing body (wrong sala for the
                          Constitutional Court relatoría, out-of-range number,
                          etc.). Flagged for human review, never rewritten.

The classifier is intentionally conservative: when in doubt it prefers
``source_unavailable`` or ``ambiguous`` over asserting ``not_found`` and never
prefers a class that would imply substituting the identifier.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re

from .common import ROOT, read_json, write_json

BACKLOG_VERSION = "acquisition-backlog-v0.6"

# Salas actually published by the Constitutional Court relatoría resolver used in
# acquisition.discover(). Anything else routed there cannot resolve, regardless
# of whether the decision exists at another court.
CONSTITUTIONAL_SALAS = {"C", "T", "SU"}
# Prefixes that identify the ordinary/administrative high courts (Corte Suprema
# de Justicia: SL labour, SP penal, SC civil; Consejo de Estado etc.). These are
# real courts, but the current resolver has no verified URL builder for them.
SUPREME_COURT_SALAS = {"SL", "SP", "SC", "AL", "AP", "STL", "STP", "STC"}


def _decision_sala(number: str) -> str | None:
    m = re.match(r"^([A-Z]+)-?\d", number or "")
    return m.group(1) if m else None


def classify_target(target: dict, *, resolved_ids: set[str]) -> dict:
    """Return an auditable classification record for one failed target.

    ``target`` is a failed entry from ``corpus/acquisition.json``. The function is
    pure and deterministic: identical input yields identical output.
    """
    doc_id = target["doc_id"]
    body = target.get("canonical_body") or []
    kind = body[0] if body else None
    number = body[1] if len(body) > 1 else None
    year = body[2] if len(body) > 2 else None
    error = target.get("error", "") or ""

    signals: list[str] = []
    resolution = "not_found"

    if doc_id in resolved_ids:
        return {"doc_id": doc_id, "resolution": "resolved", "signals": ["present_in_parsed_corpus"],
                "canonical_body": body, "norm_name": target.get("norm_name"),
                "issuing_body_hint": None, "note": "Target is present in the parsed corpus.",
                "seed_url": target.get("seed_url"), "original_error": error,
                "action_required": "none"}

    if kind == "jurisprudencia":
        sala = _decision_sala(str(number))
        seq = re.sub(r"^[A-Z]+-?", "", str(number)) if number else ""
        if sala in SUPREME_COURT_SALAS:
            resolution = "source_unavailable"
            signals.append("high_court_without_verified_resolver")
            issuing = "Corte Suprema de Justicia / Consejo de Estado"
            note = ("Ordinary/high-court decision. The official resolver only builds "
                    "Constitutional Court relatoría URLs; a manually verified source URL "
                    "for this court is required before acquisition.")
            action = "provide_verified_high_court_url"
        elif sala in CONSTITUTIONAL_SALAS:
            # Routed to the Court resolver but the downloaded page did not match
            # the requested identity. Distinguish structurally implausible single
            # or oversized sequence numbers from plausible not-found decisions.
            issuing = "Corte Constitucional"
            if seq.isdigit() and (len(seq) <= 1 or int(seq) == 0):
                resolution = "identifier_suspect"
                signals.append("implausible_decision_sequence_number")
                note = ("Constitutional Court decision sequence number is structurally "
                        "implausible (too short/zero). Seed identifier preserved; needs "
                        "human confirmation of the exact radicado before acquisition.")
                action = "human_verify_identifier"
            else:
                resolution = "not_found"
                signals.append("court_page_identity_mismatch")
                note = ("Constitutional Court page did not confirm the requested identity; "
                        "the exact decision was not found at the resolved URL. Identifier "
                        "preserved, not substituted.")
                action = "human_verify_identifier"
        else:
            resolution = "identifier_suspect"
            signals.append("unknown_decision_sala")
            issuing = None
            note = ("Decision sala prefix is not recognised for any resolver. Seed "
                    "identifier preserved for human review; never remapped to a similar sala.")
            action = "human_verify_identifier"
        return {"doc_id": doc_id, "resolution": resolution, "signals": signals,
                "canonical_body": body, "norm_name": target.get("norm_name"),
                "issuing_body_hint": issuing, "note": note, "seed_url": target.get("seed_url"),
                "original_error": error, "action_required": action}

    # Legislation / decrees / named instruments.
    if kind in {"ley", "decreto"} and number and str(number).isdigit():
        num = int(number)
        # Colombian consecutive Law/Decree numbering resets yearly and never
        # reaches five digits within a single year. A 5-digit "law number" is a
        # structural red flag for a mis-seeded identifier (e.g. a radicado or a
        # concatenation), not evidence that a similar law should be substituted.
        if kind == "ley" and num >= 10000:
            resolution = "identifier_suspect"
            signals.append("law_number_out_of_range")
            note = ("Law number is out of the plausible range for annual consecutive "
                    "numbering (>= 10000). Likely a mis-transcribed seed identifier; "
                    "preserved verbatim and flagged, never replaced by a similar law.")
            action = "human_verify_identifier"
        elif kind == "ley" and year and num > (int(year) - 1990) * 400 + 400 and int(year) >= 1991:
            # Post-1991 annual law counts stay well under a few hundred; a number
            # far above the plausible ceiling for its year is suspect.
            resolution = "identifier_suspect"
            signals.append("law_number_implausible_for_year")
            note = ("Law number is implausibly high for its stated year under annual "
                    "consecutive numbering. Seed preserved and flagged for human review.")
            action = "human_verify_identifier"
        else:
            resolution = "not_found"
            signals.append("catalogue_search_no_exact_match")
            note = ("Official catalogue search returned no exact number/year match. The "
                    "identifier is structurally plausible; it may be repealed, renumbered, "
                    "or absent from this catalogue. Not substituted.")
            action = "human_verify_or_alternate_official_source"
        issuing = "Función Pública / SUIN-Juriscol"
        return {"doc_id": doc_id, "resolution": resolution, "signals": signals,
                "canonical_body": body, "norm_name": target.get("norm_name"),
                "issuing_body_hint": issuing, "note": note, "seed_url": target.get("seed_url"),
                "original_error": error, "action_required": action}

    # Named codes / accords / instruments without a machine-resolvable number.
    resolution = "ambiguous"
    signals.append("named_instrument_without_verified_url")
    note = ("Named instrument requires a manually verified official URL; the canonical "
            "target cannot be resolved deterministically. Seed preserved.")
    return {"doc_id": doc_id, "resolution": resolution, "signals": signals,
            "canonical_body": body, "norm_name": target.get("norm_name"),
            "issuing_body_hint": None, "note": note, "seed_url": target.get("seed_url"),
            "original_error": error, "action_required": "provide_verified_official_url"}


def classify_backlog(acquisition: dict) -> dict:
    """Classify every non-downloaded target in an acquisition report."""
    documents = acquisition.get("documents", [])
    resolved_ids = {d["doc_id"] for d in documents if d.get("status") == "downloaded"}
    failed = [d for d in documents if d.get("status") != "downloaded"]
    records = [classify_target(t, resolved_ids=resolved_ids) for t in failed]
    records.sort(key=lambda r: (r["resolution"], r["doc_id"]))
    counts: dict[str, int] = {}
    for r in records:
        counts[r["resolution"]] = counts.get(r["resolution"], 0) + 1
    by_area: dict[str, dict[str, int]] = {}
    failed_by_id = {d["doc_id"]: d for d in failed}
    for r in records:
        for area in failed_by_id.get(r["doc_id"], {}).get("areas", []) or ["(sin área)"]:
            by_area.setdefault(area, {}).setdefault(r["resolution"], 0)
            by_area[area][r["resolution"]] += 1
    return {"version": BACKLOG_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_unresolved": len(failed),
            "classes": ["resolved", "not_found", "ambiguous", "source_unavailable", "identifier_suspect"],
            "counts": counts, "by_area": by_area, "targets": records,
            "policy": ("Official/public sources only. Seed identifiers are never rewritten and "
                       "no similar norm/year/number/decision is ever substituted. Unverified "
                       "identity stays unresolved with a provenance note.")}


def build_report(corpus=None) -> dict:
    corpus = corpus or (ROOT / "corpus")
    acquisition = read_json(corpus / "acquisition.json")
    report = classify_backlog(acquisition)
    write_json(ROOT / "reports/acquisition_backlog_v06.json", report)
    return report
