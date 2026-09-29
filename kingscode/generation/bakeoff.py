"""Decoder bakeoff contract over one frozen evidence file (plan B6).

Every decoder gets byte-identical evidence: the freeze is validated once, its
SHA-256 is checked before and after every decoder run, and each run records the
exact model/prompt/freeze identity. A failing decoder only fails its own run.
No selection happens here: the report is a side-by-side table.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..common import ROOT, file_hash, write_json
from .experiments import run_generation
from .retrieval_experiments import load_freeze


def evidence_sha256(passages: list[dict]) -> str:
    return hashlib.sha256(json.dumps(passages, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def run_bakeoff(aliases: list[str], freeze_path: Path, *, corpus: Path = ROOT / "corpus",
                output_root: Path = ROOT / "reports/decoders", config_path: Path = ROOT / "config/decoder_bakeoff.json",
                backends: dict | None = None) -> dict:
    freeze_path = Path(freeze_path)
    load_freeze(freeze_path, corpus=corpus)
    freeze_sha = file_hash(freeze_path)
    results = []
    for alias in aliases:
        if file_hash(freeze_path) != freeze_sha:
            raise ValueError(f"Frozen evidence changed before decoder {alias}")
        record = run_generation(alias, freeze_path=freeze_path, corpus=corpus, output_root=output_root,
                                config_path=config_path, backend=(backends or {}).get(alias))
        if file_hash(freeze_path) != freeze_sha:
            raise ValueError(f"Frozen evidence changed during decoder {alias}")
        official = (record.get("official_evaluation") or {}).get("total_automatico") or {}
        results.append({"model": alias, "status": record["status"], "revision": record.get("revision"),
                        "prompt_version": record.get("prompt_version"),
                        "evidence_sha256": (record.get("evidence") or {}).get("sha256"),
                        "fingerprint": record.get("fingerprint"), "run": record["paths"]["run"],
                        "official_without_ragas": official.get("obtenidos"),
                        "metrics": record.get("metrics"), "error": record.get("error")})
    identical = all(r["evidence_sha256"] in (None, freeze_sha) for r in results)
    report = {"freeze_sha256": freeze_sha, "evidence_identical_across_decoders": identical, "results": results,
              "table": [[r["model"], r["status"], r["official_without_ragas"], (r["metrics"] or {}).get("valid_json_rate"),
                         (r["metrics"] or {}).get("abstentions"), (r["metrics"] or {}).get("latency_p50_ms")] for r in results],
              "table_columns": ["model", "status", "official_without_ragas", "valid_json_rate", "abstentions", "latency_p50_ms"],
              "selection": "none: contract report only; selection rule lives in the predeclared experiment spec"}
    write_json(Path(output_root) / f"bakeoff-{freeze_sha[:12]}.json", report)
    return report
