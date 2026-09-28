"""Independent second pass: fresh rebuild, byte hashes and separate metric arithmetic.

Run after the main build/benchmark/tests. The temporary rebuilt corpus is kept
for inspection. Official files are read only.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def main():
    baseline = json.loads((ROOT / "corpus/manifest.json").read_text(encoding="utf-8"))
    checks = {}
    for line in (ROOT / "docs/OFFICIAL_SHA256.txt").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            expected, name = line.split("  ", 1)
            if sha(ROOT / name) != expected:
                raise RuntimeError(f"Official hash changed: {name}")
            checks[name] = expected
    out = ROOT / "tmp/member_a_second_rebuild"
    out.mkdir(parents=True, exist_ok=True)
    # Do not use the first pass's serialized BM25 or graph to rebuild.
    (out / "acquisition.json").write_bytes((ROOT / "corpus/acquisition.json").read_bytes())
    subprocess.run([sys.executable, str(ROOT / "tools/member_a.py"), "build", "--corpus", str(out)], check=True, cwd=ROOT)
    artifacts = ["passages.jsonl", "graph/nodes.jsonl", "graph/edges.jsonl", "index/bm25.json"]
    compared = {}
    for rel in artifacts:
        actual, expected = sha(out / rel), sha(ROOT / "corpus" / rel)
        if actual != expected:
            raise RuntimeError(f"Rebuild not byte-identical: {rel}")
        compared[rel] = actual
    passages = rows(ROOT / "corpus/passages.jsonl")
    by_id = {p["passage_id"]: p for p in passages}
    # Independently recompute exact-slice provenance and boundary safety.
    for d in baseline["documentos"]:
        raw, clean = ROOT / d["raw_path"], ROOT / d["clean_path"]
        if sha(raw) != d["source_sha256"] or sha(clean) != d["sha256"]:
            raise RuntimeError("Source trace failed")
        text = clean.read_text(encoding="utf-8")
        for p in [p for p in passages if p["doc_id"] == d["doc_id"]]:
            a, z = p["clean_start"], p["clean_end"]
            if not (0 <= a < z <= len(text)) or p["text"] != p["text_prefix"] + text[a:z]:
                raise RuntimeError("Second-pass offset check failed")
    report = json.loads((ROOT / "reports/retrieval_bm25.json").read_text(encoding="utf-8"))
    if report["corpus_hashes"] != baseline["hashes"]:
        raise RuntimeError("Benchmark refers to a different corpus")
    audit = {x["id"]: x for x in json.loads((ROOT / "reports/legal_basis_audit.json").read_text(encoding="utf-8"))}
    predictions = rows(ROOT / "reports/retrieval_bm25_per_question.jsonl")
    metric_checks = {}
    for mode in ["off", "auto", "on"]:
        recalls, reciprocal = [], []
        for result in [x for x in predictions if x["graph_mode"] == mode]:
            gold = {tuple(t) for t in audit[result["id"]]["targets"]}
            if not gold:
                continue
            matched, first = set(), None
            for rank, pid in enumerate(result["passage_ids"], 1):
                p = by_id[pid]
                hits = {t for t in gold if list(t[:3]) == p["canonical_body"] and (t[3] is None or t[3] == p["article"])}
                matched.update(hits)
                if hits and first is None:
                    first = rank
            recalls.append(len(matched) / len(gold))
            reciprocal.append(1 / first if first else 0)
        recall, mrr = sum(recalls) / len(recalls), sum(reciprocal) / len(reciprocal)
        if abs(recall - report["runs"][mode]["Recall@10"]) > 1e-12 or abs(mrr - report["runs"][mode]["MRR@10"]) > 1e-12:
            raise RuntimeError("Independent metric calculation differs")
        metric_checks[mode] = {"Recall@10": recall, "MRR@10": mrr}
    # A new interpreter must reproduce all 50 rankings without reading labels.
    sys.path.insert(0, str(ROOT))
    from kingscode.retrieval import Retriever
    retriever = Retriever()
    sample = {r["id"]: r["pregunta"] for r in rows(ROOT / "data/sample_50.jsonl")}
    for result in predictions:
        ids = [p["passage_id"] for p in retriever.retrieve(sample[result["id"]], 10, result["graph_mode"])]
        if ids != result["passage_ids"]:
            raise RuntimeError("Second-process ranking mismatch")
    result = {"ok": True, "timestamp": datetime.now(timezone.utc).isoformat(),
              "official_hashes_verified": len(checks), "rebuilt_from_raw": True,
              "byte_identical_artifacts": compared, "independent_offsets": len(passages),
              "independent_metrics": metric_checks, "repeated_rankings": len(predictions)}
    (ROOT / "reports/member_a_second_verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
