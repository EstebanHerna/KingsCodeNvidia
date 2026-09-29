"""Freeze planner outputs once; every retrieval comparison replays the same plans.

reports/query_plans/<experiment_id>/
  manifest.json   model id/revision, tokenizer revision, prompt version + SHA-256,
                  generation config, environment, question-set SHA-256, counts
  plans.jsonl     one QueryPlan record per question id
experiment_id is derived from the manifest identity, so the same model, prompt,
config and question set always map to the same directory.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys

from ..common import ROOT
from .batch import atomic_write_text
from .planner import PLANNER_PROMPT_VERSION, QueryPlan, build_planner_messages, plan_from_output, prompt_sha256, question_sha256

PLANS_ROOT = ROOT / "reports/query_plans"


def question_set_sha256(items: list[tuple]) -> str:
    payload = json.dumps([[str(i), t] for i, t in items], ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def planner_identity(backend, items: list[tuple]) -> dict:
    return {"planner_prompt_version": PLANNER_PROMPT_VERSION, "planner_prompt_sha256": prompt_sha256(),
            "backend": backend.identity(), "question_set_sha256": question_set_sha256(items),
            "questions": len(items)}


def experiment_id(identity: dict) -> str:
    return hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def freeze_plans(items: list[tuple], backend, *, root: Path = PLANS_ROOT) -> Path:
    """items: (question_id, question_text) only; labels never reach the planner."""
    if len({str(i) for i, _ in items}) != len(items):
        raise ValueError("Duplicate question ids")
    identity = planner_identity(backend, items)
    out = Path(root) / experiment_id(identity)
    plans_path = out / "plans.jsonl"
    done = {}
    if plans_path.exists():  # resumable: keep plans already produced under this identity
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        if manifest["identity"] != identity:
            raise ValueError("Existing plans were produced under a different identity")
        done = {r["question_id"]: r for r in (json.loads(l) for l in plans_path.read_text(encoding="utf-8").splitlines() if l.strip())}
    records = []
    for qid, text in items:
        record = done.get(str(qid))
        if record is None or record["question_sha256"] != question_sha256(text):
            raw, usage = backend.complete(build_planner_messages(text))
            record = {**plan_from_output(qid, text, raw).record(), "usage": usage}
        records.append(record)
        atomic_write_text(plans_path, "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records))
    ok = sum(r["status"] == "ok" for r in records)
    rates = [r["preservation"]["rate"] for r in records if r["status"] == "ok" and r["preservation"].get("rate") is not None]
    manifest = {"identity": identity, "experiment_id": out.name,
                "environment": {"python": sys.version.split()[0], "platform": platform.platform(),
                                "runtime": backend.identity().get("environment", {})},
                "counts": {"questions": len(records), "ok": ok, "fallback_malformed": len(records) - ok,
                           "with_generated_references": sum(bool(r["generated_references"]) for r in records),
                           "mean_preservation_rate": (sum(rates) / len(rates)) if rates else None},
                "plans_sha256": hashlib.sha256(plans_path.read_bytes()).hexdigest()}
    atomic_write_text(out / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return out


class PlanStore:
    """Replay mode: plans are read, never regenerated. Refuses mismatched questions."""

    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.manifest = json.loads((self.directory / "manifest.json").read_text(encoding="utf-8"))
        data = (self.directory / "plans.jsonl").read_bytes()
        if hashlib.sha256(data).hexdigest() != self.manifest["plans_sha256"]:
            raise ValueError("plans.jsonl does not match its manifest hash")
        self.plans = {r["question_id"]: QueryPlan.from_record(r)
                      for r in (json.loads(l) for l in data.decode("utf-8").splitlines() if l.strip())}

    def get(self, question_id, question_text: str) -> QueryPlan:
        plan = self.plans.get(str(question_id))
        if plan is None:
            raise KeyError(f"No frozen plan for question {question_id}")
        if plan.question_sha256 != question_sha256(question_text):
            raise ValueError(f"Frozen plan for {question_id} was made for a different question text")
        return plan
