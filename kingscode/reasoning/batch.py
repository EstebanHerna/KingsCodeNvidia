"""Robust batch execution for the 992 blind questions (plan B7).

One bad question never takes the others down:
- every answered item is checkpointed atomically (temp file + os.replace);
- resume skips items whose checkpoint still validates, under the same identity;
- an exception is isolated to its item, recorded in errors/<id>.json and retried
  deterministically (same configuration) up to `retries` more times;
- an item that still fails gets a valid abstention row (reason pipeline_error);
- submissions.jsonl is assembled sorted by id, checked for completeness (every
  input id, no duplicates, schema-valid) and written atomically with its hash.

Gate 1B's run_experiment is untouched: this is a separate runner.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from time import perf_counter
import traceback

from .contracts import ANSWER_FIELDS, Question
from .decoder import abstention_row
from .guards import validate_submission
from .official import official_bodies

FALLBACK_REASON = "pipeline_error"
# Decoder failures that a deterministic retry reproduces; retrying only costs GPU time.
DETERMINISTIC_CODES = {"INVALID_MODEL_OUTPUT", "CONTEXT_LIMIT_EXCEEDED"}


def _dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def questions_sha256(questions: list[Question]) -> str:
    return hashlib.sha256(_dumps([q.public_record() for q in questions]).encode("utf-8")).hexdigest()


def synthetic_questions(questions: list[Question], n: int = 992, id_offset: int = 100000) -> list[Question]:
    """Rehearsal set: the given questions repeated with new, unique ids."""
    return [Question(id_offset + i, q.text, q.format, dict(q.options)) for i, q in enumerate(questions[i % len(questions)] for i in range(n))]


def answer_text(row: dict) -> str:
    """Same fields the official evaluator reads citations from."""
    return " ".join(str(row.get(k) or "") for k in {
        "multiple_choice": ("justificacion",), "semi_open": ("respuesta", "referencia_legal"),
        "open_ended": ANSWER_FIELDS["open_ended"]}.get(row.get("formato"), ()))


def _valid_checkpoint(path: Path, question: Question):
    try:
        item = json.loads(path.read_text(encoding="utf-8"))
        row = item["row"]
        if row.get("id") != question.id or row.get("formato") != question.format:
            return None
        validate_submission(row)
        return item
    except Exception:
        return None


class BatchRunner:
    def __init__(self, pipeline, run_dir: Path, *, identity: dict | None = None, retries: int = 2):
        if type(retries) is not int or not 0 <= retries <= 2:
            raise ValueError("retries must be 0, 1 or 2")
        self.pipeline, self.run_dir, self.retries = pipeline, Path(run_dir), retries
        self.identity = dict(identity or {})

    def _check_identity(self, questions: list[Question], resume: bool) -> dict:
        identity = {**self.identity, "questions_sha256": questions_sha256(questions)}
        path = self.run_dir / "identity.json"
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if not resume:
                raise FileExistsError(f"{self.run_dir} already holds a run; pass resume=True or use a new directory")
            if existing != identity:
                raise ValueError("Refusing to resume: run identity (questions/config) differs from the checkpoints")
        else:
            atomic_write_text(path, json.dumps(identity, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        return identity

    def _attempt(self, question: Question):
        errors = []
        for attempt in range(1 + self.retries):
            try:
                row, trace = self.pipeline.run(question)
                return row, trace, errors
            except Exception as exc:  # isolation is the point; KeyboardInterrupt/SystemExit still stop the run
                errors.append({"attempt": attempt + 1, "type": type(exc).__name__, "code": getattr(exc, "code", None),
                               "message": str(exc), "traceback": traceback.format_exc()})
                if getattr(exc, "code", None) in DETERMINISTIC_CODES:
                    break  # temperature 0: the same input reproduces the same output
        return None, None, errors

    def run(self, questions: list[Question], *, resume: bool = True) -> dict:
        started = perf_counter()
        ids = [q.id for q in questions]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate question ids in the input")
        identity = self._check_identity(questions, resume)
        counts = {"resumed": 0, "answered": 0, "retried_ok": 0, "fallback": 0}
        for question in questions:
            item_path = self.run_dir / "items" / f"{question.id}.json"
            if resume and item_path.exists() and _valid_checkpoint(item_path, question):
                counts["resumed"] += 1
                continue
            row, trace, errors = self._attempt(question)
            status = "ok"
            if errors:
                atomic_write_text(self.run_dir / "errors" / f"{question.id}.json",
                                  json.dumps({"id": question.id, "attempts": errors}, ensure_ascii=False, indent=2) + "\n")
            if row is None:
                # Formal abstention only: the schema's "A" placeholder is never scored
                # because the official score_closed requires abstencion=false.
                row, status = abstention_row(question, [], FALLBACK_REASON), "fallback"
                trace = {"abstention_reason": FALLBACK_REASON, "abstention_source": "pipeline_error",
                         "error_codes": [e["code"] or e["type"] for e in errors]}
                counts["fallback"] += 1
            elif errors:
                counts["retried_ok"] += 1
            else:
                counts["answered"] += 1
            validate_submission(row)
            atomic_write_text(item_path, _dumps({"row": row, "status": status, "attempts": len(errors) + (status == "ok"),
                                                  "trace": trace}) + "\n")
            done = sum(counts.values())
            elapsed = perf_counter() - started
            # Progress goes to stderr so stdout stays a single JSON report.
            print(f"[batch] {done}/{len(questions)} id={question.id} {question.format} {status}"
                  f"{' abstencion' if row.get('abstencion') else ''} | {elapsed:.0f} s, {elapsed / done:.1f} s/pregunta",
                  file=sys.stderr, flush=True)
        report = self.assemble(questions)
        report.update(counts=counts, identity=identity, diagnostics=self.diagnostics(questions),
                      seconds=perf_counter() - started,
                      finished_at=datetime.now(timezone.utc).isoformat())
        atomic_write_text(self.run_dir / "batch_report.json", json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n")
        return report

    def diagnostics(self, questions: list[Question]) -> dict:
        """Aggregate rates over per-item traces (kept intact in items/<id>.json)."""
        from collections import Counter
        n = len(questions)
        sources, attribution, normalization, actions, codes, warnings = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
        before = after = fallbacks = tokens_in = tokens_out = 0
        gen_ms = []
        for q in questions:
            item = json.loads((self.run_dir / "items" / f"{q.id}.json").read_text(encoding="utf-8"))
            trace = item.get("trace") or {}
            d = trace.get("diagnostics") or {}
            sources[trace.get("abstention_source", "none")] += 1
            attribution[d.get("attribution_status", "none")] += 1
            if d.get("normalization_action"):
                normalization[d["normalization_action"]] += 1
            actions.update(d.get("repair_actions") or {})
            # "semi_open_sentences_2_outside_3_5" -> "semi_open_sentences_outside_3_5"
            warnings.update(re.sub(r"_\d+_(?=outside|over)", "_", w) for w in d.get("format_warnings") or [])
            codes.update(trace.get("error_codes") or [])
            before += d.get("citations_before_repair") or 0
            after += d.get("citations_after_repair") or 0
            fallbacks += bool(trace.get("citation_guard_fallback"))
            tokens_in += d.get("input_tokens") or 0
            tokens_out += d.get("output_tokens") or 0
            if d.get("generation_ms") is not None:
                gen_ms.append(d["generation_ms"])
        rate = lambda c: {k: {"n": v, "rate": v / n} for k, v in sorted(c.items())}
        return {"questions": n, "abstention_source": rate(sources), "attribution_status": rate(attribution),
                "normalization_action": rate(normalization), "repair_actions": dict(sorted(actions.items())),
                "pipeline_error_codes": dict(sorted(codes.items())), "format_warnings": rate(warnings),
                "citations_before_repair": before, "citations_after_repair": after,
                "citation_guard_fallback_rate": fallbacks / n if n else 0.0,
                "input_tokens": tokens_in, "output_tokens": tokens_out,
                "generation_ms_p50": sorted(gen_ms)[len(gen_ms) // 2] if gen_ms else None,
                "note": "Label-free diagnostics; no thresholds derived from the official 50."}

    def assemble(self, questions: list[Question]) -> dict:
        rows, missing, fallback_ids = [], [], []
        for question in sorted(questions, key=lambda q: q.id):
            item = _valid_checkpoint(self.run_dir / "items" / f"{question.id}.json", question)
            if item is None:
                missing.append(question.id)
                continue
            rows.append(item["row"])
            if item.get("status") == "fallback":
                fallback_ids.append(question.id)
        out_ids = [r["id"] for r in rows]
        complete = not missing and len(out_ids) == len(set(out_ids)) == len(questions)
        if not complete:
            raise RuntimeError(f"Incomplete submission: {len(missing)} missing ids, e.g. {missing[:10]}")
        text = "".join(_dumps(r) + "\n" for r in rows)
        atomic_write_text(self.run_dir / "submissions.jsonl", text)
        return {"submission": str(self.run_dir / "submissions.jsonl"), "rows": len(rows), "complete": True,
                "duplicates": 0, "schema_errors": 0, "fallback_ids": fallback_ids,
                "submission_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}


def verify_items(pipeline, questions: list[Question], delivered: Path, only: list[int]) -> dict:
    """Live-verification mode: regenerate selected ids sequentially (concurrency 1)
    and compare cited norms and retrieved passages with the delivered file."""
    by_id = {q.id: q for q in questions}
    delivered_rows = {}
    for line in Path(delivered).read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            delivered_rows[row["id"]] = row
    results = []
    for qid in only:
        if qid not in by_id or qid not in delivered_rows:
            results.append({"id": qid, "status": "unknown_id"})
            continue
        new, _ = pipeline.run(by_id[qid])
        old = delivered_rows[qid]
        passages_equal = [p.get("passage_id") for p in new["pasajes_recuperados"]] == [p.get("passage_id") for p in old["pasajes_recuperados"]]
        citations_equal = official_bodies(answer_text(new)) == official_bodies(answer_text(old))
        results.append({"id": qid, "passages_equal": passages_equal, "citations_equal": citations_equal,
                        "row_identical": _dumps(new) == _dumps(old),
                        "status": "match" if passages_equal and citations_equal else "MISMATCH"})
    return {"checked": len(results), "all_match": all(r.get("status") == "match" for r in results), "results": results}
