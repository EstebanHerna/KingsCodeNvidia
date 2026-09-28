"""Boundary to the unchanged official evaluator; no RAGAS/network/model loading."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from ..common import ROOT
from .guards import validate_submission


def official_hashes() -> dict:
    checked = {}
    for line in (ROOT / "docs/OFFICIAL_SHA256.txt").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            expected, name = line.split("  ", 1)
            actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError(f"Official file changed: {name}")
            checked[name] = actual
    return checked


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def run_eval(submission: str | Path, *, timeout: int = 60) -> dict:
    """Evaluate all sample_50 rows, fail if malformed/incomplete; never edit them."""
    path = Path(submission).resolve()
    original = path.read_bytes()
    official_hashes()
    rows = [json.loads(line, object_pairs_hook=_unique_pairs) for line in original.decode("utf-8").splitlines() if line.strip()]
    for row in rows:
        validate_submission(row)
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate submission IDs")
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/evaluate.py"), "--submission", str(path), "--split", "sample"],
                          cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=timeout,
                          env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
    if path.read_bytes() != original:
        raise RuntimeError("Submission changed during evaluation")
    if proc.returncode:
        raise RuntimeError(f"Official evaluator failed with exit code {proc.returncode}")
    report = json.loads(proc.stdout)
    if report["validacion"]["errores"]:
        raise ValueError(f"Official evaluator rejected submission: {report['validacion']}")
    return report
