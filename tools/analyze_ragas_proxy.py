"""Free, local proxy of the RAGAS free-text component (no OpenRouter, no credit).

    python tools/analyze_ragas_proxy.py <run>/batch/submissions.jsonl [<other>.jsonl ...]

Official RAGAS answer_correctness = LLM factual agreement (judge, paid) + semantic similarity
computed by a LOCAL open encoder (intfloat/multilingual-e5-large). This tool reproduces the
free part exactly as the evaluator builds it (same text per format, same reference, abstention
= 0, denominator = all judged items) and adds a token-F1 overlap as a crude factual proxy.

Use it to RANK variants between GPU runs; spend the real --ragas only on the final candidate.
Calibration point (2026-10-02): run qwen3-8b_bm25_..._20261002_111603 -> official RAGAS 0.4275.
Reads respuesta_esperada from data/sample_50.jsonl for measurement only (allowed for analyze_*).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ENCODER = "intfloat/multilingual-e5-large"


def ragas_text(sub: dict) -> str:  # identical to scripts/evaluate.py::ragas_text
    if sub.get("formato") == "semi_open":
        return str(sub.get("respuesta") or "")
    return " ".join(str(sub.get(k) or "") for k in ("marco_normativo", "analisis", "jurisprudencia", "conclusion"))


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-záéíóúñü0-9]+", text.lower()) if len(t) > 2]


def token_f1(answer: str, truth: str) -> float:
    a, t = _tokens(answer), _tokens(truth)
    if not a or not t:
        return 0.0
    common = sum(min(a.count(w), t.count(w)) for w in set(a))
    if not common:
        return 0.0
    p, r = common / len(a), common / len(t)
    return 2 * p * r / (p + r)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("submissions", type=Path, nargs="+")
    parser.add_argument("--no-encoder", action="store_true", help="token-F1 only (no model download)")
    args = parser.parse_args(argv)
    key = {}
    for line in (ROOT / "data/sample_50.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if r["formato"] != "multiple_choice":
                key[int(r["id"])] = r
    model = None
    if not args.no_encoder:
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(ENCODER)
        except Exception as exc:  # missing package/model: degrade visibly
            print(f"[proxy] encoder unavailable ({type(exc).__name__}); token-F1 only", file=sys.stderr)
    for path in args.submissions:
        subs = {int(json.loads(l)["id"]): json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()}
        sims, f1s, answered = [], [], 0
        pairs = []
        for qid, k in key.items():
            s = subs.get(qid)
            if not s or s.get("abstencion"):
                sims.append(0.0); f1s.append(0.0)
                continue
            answered += 1
            pairs.append((len(sims), "query: " + ragas_text(s), "query: " + str(k.get("respuesta_esperada") or "")))
            sims.append(None); f1s.append(token_f1(ragas_text(s), str(k.get("respuesta_esperada") or "")))
        if model is not None and pairs:
            import numpy as np
            a = model.encode([p[1] for p in pairs], normalize_embeddings=True)
            b = model.encode([p[2] for p in pairs], normalize_embeddings=True)
            for (i, _, _), x, y in zip(pairs, a, b):
                sims[i] = float(np.dot(x, y))
        n = len(key)
        result = {"run": str(path), "judged": n, "answered": answered,
                  "token_f1_mean": round(sum(f1s) / n, 4),
                  "semantic_similarity_mean": round(sum(s or 0.0 for s in sims) / n, 4) if model is not None else None}
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
