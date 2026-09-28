"""Blocking schema/citation gates with exact evidence projection and provenance."""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import json
import math

from jsonschema import Draft202012Validator

from ..common import ROOT, read_json
from .contracts import ANSWER_FIELDS
from .legal import references, supporting_passages

GUARD_VERSION = "source-article-guard-v1"


class SubmissionValidationError(ValueError):
    pass


class CitationGuardError(ValueError):
    def __init__(self, report: dict):
        self.report = report
        super().__init__("Unsupported citation or altered evidence; output rejected")


@lru_cache(maxsize=1)
def schema_validator():
    schema = read_json(ROOT / "schema/submission.schema.json")
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_submission(row: dict) -> None:
    try:
        encoded = json.dumps(row, ensure_ascii=False, allow_nan=False)
        if json.loads(encoded) != row:
            raise ValueError("Output contains non-JSON types/keys")
    except (ValueError, TypeError) as exc:
        raise SubmissionValidationError("Output is not strict JSON") from exc
    errors = sorted(schema_validator().iter_errors(row), key=lambda e: str(list(e.path)))
    if errors:
        raise SubmissionValidationError("; ".join(f"{list(e.path)}: {e.message}" for e in errors))
    if type(row["id"]) is not int:
        raise SubmissionValidationError("id must be a JSON integer")
    # Additional B safety gates implement requirements written in the official
    # descriptions but not encoded as JSON Schema constraints.
    if len(row["pasajes_recuperados"]) > 10:
        raise SubmissionValidationError("At most ten evidence passages may support a response")
    if not row["abstencion"] and not row["pasajes_recuperados"]:
        raise SubmissionValidationError("Non-abstaining output requires evidence")
    if not row["abstencion"]:
        if any(row.get(k) in (None, "", [], {}) for k in ANSWER_FIELDS[row["formato"]]):
            raise SubmissionValidationError("Non-abstaining output has empty required answer fields")
    if any(k in row for k in ("expected_answer", "legal_basis", "respuesta_esperada", "texto_respuesta_correcta")):
        raise SubmissionValidationError("Evaluation labels may not appear in a submission")


def check_passages(passages: list[dict]) -> None:
    required = ("passage_id", "doc_id", "text", "norm_name", "source_url")
    for p in passages:
        if not isinstance(p, dict) or any(not isinstance(p.get(k), str) or not p[k].strip() for k in required):
            raise ValueError("Passage does not satisfy A's source/text/identity contract")
        if not isinstance(p.get("hierarchy_path"), list) or not isinstance(p.get("graph_node_ids"), list):
            raise ValueError("Passage missing hierarchy/graph metadata")
        if any(k in p for k in ("expected_answer", "legal_basis", "respuesta_correcta", "respuesta_esperada")):
            raise ValueError("Evaluation label in evidence")


def evidence_record(p: dict) -> dict:
    result = {"doc_id": p["doc_id"], "texto": p["text"], "passage_id": p["passage_id"],
              "source_url": p["source_url"], "norm_name": p["norm_name"], "article": p.get("article"),
              "hierarchy_path": deepcopy(p["hierarchy_path"]), "graph_node_ids": list(p["graph_node_ids"])}
    for key in ("canonical_body", "source_sha256", "retrieved_at", "source_pages"):
        if key in p:
            result[key] = deepcopy(p[key])
    if p.get("score") is not None:
        if isinstance(p["score"], bool) or not isinstance(p["score"], (int, float)) or not math.isfinite(p["score"]):
            raise ValueError("Nonfinite/non-numeric retrieval score")
        result["score"] = p["score"]
    # Official offsets refer to the whole literal texto. A's text_prefix is not
    # part of its clean interval, so omit optional inicio/fin rather than mislabel.
    return result


def _strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _strings(child, f"{path}.{key}" if path else key)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from _strings(child, f"{path}[{i}]")


def citation_guard(row: dict, passages: list[dict]) -> dict:
    """Never repair/mutate row; reject any unsupported reference/evidence record."""
    validate_submission(row)
    check_passages(passages)
    sources = {}
    for p in passages:
        if p["passage_id"] in sources and p != sources[p["passage_id"]]:
            raise ValueError("Conflicting passage IDs cannot authenticate evidence")
        sources[p["passage_id"]] = p
    emitted, issues, seen = [], [], set()
    for e in row["pasajes_recuperados"]:
        p = sources.get(e.get("passage_id"))
        if p is None or e != evidence_record(p) or p.get("retrieval_eligible") is False or p.get("is_current_text") is False:
            issues.append({"kind": "evidence_mismatch", "passage_id": e.get("passage_id")})
        elif p["passage_id"] in seen:
            issues.append({"kind": "duplicate_evidence", "passage_id": p["passage_id"]})
        else:
            emitted.append(p)
            seen.add(p["passage_id"])
    claims, unsupported = [], 0
    for field, text in _strings({k: v for k, v in row.items() if k not in {"pasajes_recuperados", "id", "formato", "abstencion", "latencia_ms"}}):
        for ref in references(text):
            support = supporting_passages(ref, emitted)
            # Metadata cannot create a citation absent from the displayed text.
            support = [p for p in support if any(
                (ref.body is None or r.body == ref.body) and (ref.article is None or r.article == ref.article)
                for r in references(p["text"])) or (
                ref.article is not None and ref.body is not None
                and any(r.body == ref.body for r in references(p["text"]))
                and any(r.article == ref.article for r in references(p["text"])))]
            if not support:
                unsupported += 1
            claims.append({"field": field, "reference": ref.record(), "supported": bool(support),
                           "support": [{"passage_id": p["passage_id"], "doc_id": p["doc_id"],
                                        "source_url": p["source_url"], "norm_name": p["norm_name"],
                                        "article": p.get("article"), "canonical_body": p.get("canonical_body")} for p in support]})
    if not row["abstencion"] and not claims:
        issues.append({"kind": "non_abstaining_answer_without_verifiable_citation"})
    report = {"ok": not issues and unsupported == 0, "version": GUARD_VERSION,
              "citation_count": len(claims), "unsupported_count": unsupported, "evidence_issues": issues, "citations": claims}
    if not report["ok"]:
        raise CitationGuardError(report)
    return report
