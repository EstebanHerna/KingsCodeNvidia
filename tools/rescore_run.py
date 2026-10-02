"""Offline re-scoring of a saved batch run: no GPU, no decoder, no retrieval.

    python tools/rescore_run.py <run>/batch --cite-mentions 3
    python tools/rescore_run.py <run>/batch --cite-mentions 0      # baseline: must equal the run

Rebuilds only deterministic post-processing (citation builder + guard) on the SAME model
answers and the SAME retrieved evidence stored in items/<id>.json, writes a new
submissions file and runs the official evaluator (without RAGAS). The decoder output is
not regenerated, so this measures citation post-processing only, in seconds.

Limits: answers are the final rows (already repaired); builder citations are re-added on
top. Changes to prompts, retrieval or decoder still need a real GPU run.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT  # noqa: E402
from kingscode.reasoning.citation_builder import mentioned_references  # noqa: E402
from kingscode.reasoning.guards import CitationGuardError, citation_guard, validate_submission  # noqa: E402
from kingscode.reasoning.official import official_bodies  # noqa: E402


def _evidence(row: dict) -> list[dict]:
    """Guard-compatible passages rebuilt from the official evidence records."""
    out = []
    for p in row["pasajes_recuperados"]:
        q = dict(p)
        q["text"] = p.get("texto") or ""
        out.append(q)
    return out


def rescore(batch: Path, mentions: int) -> tuple[list[dict], dict]:
    rows, stats = [], {"items": 0, "changed": 0, "mentions_added": 0, "guard_rejected": 0}
    for item_path in sorted((batch / "items").glob("*.json"), key=lambda p: int(p.stem)):
        item = json.loads(item_path.read_text(encoding="utf-8"))
        row = deepcopy(item["row"])
        stats["items"] += 1
        d = (item.get("trace") or {}).get("diagnostics") or {}
        if mentions and not row["abstencion"] and row["formato"] in {"semi_open", "multiple_choice"}:
            evidence = _evidence(row)
            used = d.get("evidence_ids_used") or None
            field = "referencia_legal" if row["formato"] == "semi_open" else "justificacion"
            current = " ".join(str(row.get(k) or "") for k in ("referencia_legal", "justificacion", "respuesta"))
            extra = mentioned_references(evidence, used, current, mentions)
            if extra:
                candidate = deepcopy(row)
                if row["formato"] == "semi_open":
                    base = (row.get("referencia_legal") or "").strip()
                    candidate[field] = "; ".join([x for x in [base] if x] + extra)
                else:
                    just = (row.get("justificacion") or "").rstrip()
                    candidate[field] = just + " Normas mencionadas en la evidencia: " + "; ".join(extra) + "."
                try:
                    citation_guard(candidate, evidence, allow_body_mentions=True)
                    validate_submission(candidate)
                    row = candidate
                    stats["changed"] += 1
                    stats["mentions_added"] += len(extra)
                except (CitationGuardError, ValueError):
                    stats["guard_rejected"] += 1
        rows.append(row)
    return rows, stats


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("batch", type=Path)
    parser.add_argument("--cite-mentions", type=int, default=3)
    parser.add_argument("--split", default="sample")
    args = parser.parse_args(argv)
    rows, stats = rescore(args.batch, args.cite_mentions)
    out_dir = args.batch.parent / f"rescore_mentions{args.cite_mentions}"
    out_dir.mkdir(parents=True, exist_ok=True)
    sub = out_dir / "submissions.jsonl"
    with sub.open("w", encoding="utf-8", newline="\n") as stream:
        for r in rows:
            stream.write(json.dumps(r, ensure_ascii=False) + "\n")
    ev = out_dir / "evaluation_official.json"
    subprocess.run([sys.executable, str(ROOT / "scripts/evaluate.py"), "--submission", str(sub), "--split", args.split,
                    "--out", str(ev)], check=True, capture_output=True, text=True, encoding="utf-8")
    e = json.loads(ev.read_text(encoding="utf-8"))
    result = {**stats, "total_sin_ragas": e["total_automatico"]["obtenidos"], "cerradas": e["cerradas"]["puntos"],
              "citas": e["citas"]["puntos"], "recall": e["citas"]["recall_citas_ponderado"],
              "sin_respaldo": e["citas"]["tasa_sin_respaldo"], "abstencion": e["abstencion"]["puntos"],
              "submission": str(sub)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
