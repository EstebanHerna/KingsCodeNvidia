"""Independent Gate 1B audit and fresh-process replay; no A/B internals reused.

This verification tool reads corpus artifacts only to authenticate emitted
evidence, not to implement B's runtime retrieval or graph traversal.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, help="Run directory; defaults to most recent passing run")
    args = parser.parse_args()
    run = args.run
    if run is None:
        candidates = sorted((ROOT / "reports/member_b").glob("*/experiment.json"))
        run = next((p.parent for p in reversed(candidates) if load(p)["status"] == "passed"), None)
    if run is None:
        raise RuntimeError("Run tools/member_b.py smoke first")
    first = load(run / "experiment.json")
    if first["status"] != "passed":
        raise RuntimeError("Cannot certify a failed run")
    official = {}
    for line in (ROOT / "docs/OFFICIAL_SHA256.txt").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            expected, name = line.split("  ", 1)
            if sha(ROOT / name) != expected:
                raise RuntimeError(f"Official hash mismatch: {name}")
            official[name] = expected
    a_paths = [f"kingscode/{name}.py" for name in ["__init__", "acquisition", "common", "corpus", "evaluation", "neural", "retrieval", "validation"]]
    a_paths += ["config/corpus_passage.schema.json", "config/legal_graph.schema.json", "config/sources.json", "config/neural.json",
                "tools/member_a.py", "tests/test_knowledge.py"]
    unchanged = {}
    for path in a_paths:
        # Baseline is the original member A delivery, not the working tree.
        original = subprocess.check_output(["git", "show", f"382c5eb75106183af21c53ddfe96647c4ae97171:{path}"], cwd=ROOT)
        if original != (ROOT / path).read_bytes():
            raise RuntimeError(f"Member A implementation changed: {path}")
        unchanged[path] = sha(ROOT / path)
    # Gate 2-Prep adds decoder locks. Preserve both original retrieval entries,
    # while allowing those additive records without falsely failing Gate 1B.
    original_locks = json.loads(subprocess.check_output(
        ["git", "show", "382c5eb75106183af21c53ddfe96647c4ae97171:config/models.lock.json"], cwd=ROOT))
    current_locks = load(ROOT / "config/models.lock.json")
    if any(current_locks.get(name) != entry for name, entry in original_locks.items()):
        raise RuntimeError("Member A retrieval model locks changed")
    corpus = Path(first["settings"]["corpus_dir"])
    manifest = load(corpus / "manifest.json")
    for path, expected in manifest["hashes"].items():
        if sha(corpus / path) != expected:
            raise RuntimeError(f"Corpus artifact changed: {path}")
    if sha(corpus / "index/bm25.json") != manifest["bm25_sha256"]:
        raise RuntimeError("BM25 artifact changed")
    if first["identity"]["corpus"]["passages_sha256"] != manifest["hashes"]["passages.jsonl"]:
        raise RuntimeError("Experiment refers to another corpus")
    for path, expected in first["identity"]["implementation_sha256"].items():
        if sha(ROOT / path) != expected:
            raise RuntimeError("B code changed after experiment; run smoke again")
    submissions = rows(run / "submissions.jsonl")
    public = rows(run / "questions.jsonl")
    expected = {r["id"]: r["formato"] for r in rows(ROOT / "data/sample_50.jsonl")}
    if len(submissions) != 50 or len({r["id"] for r in submissions}) != 50 or {r["id"]: r["formato"] for r in submissions} != expected:
        raise RuntimeError("Missing/duplicate sample rows or mismatched formats")
    if any(set(r) != {"id", "pregunta", "formato", "opciones"} for r in public):
        raise RuntimeError("Non-public fields crossed the input boundary")
    validator = Draft202012Validator(load(ROOT / "schema/submission.schema.json"))
    # Independent matching against the source artifact, not B's projection helper.
    wanted = {p["passage_id"] for row in submissions for p in row["pasajes_recuperados"]}
    original_passages = {}
    with (corpus / "passages.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            p = json.loads(line)
            if p["passage_id"] in wanted:
                original_passages[p["passage_id"]] = p
    evidence_checks = 0
    for row in submissions:
        validator.validate(row)
        if row["abstencion"] is not True or len(row["pasajes_recuperados"]) > 10:
            raise RuntimeError("Dummy produced a substantive answer/too much evidence")
        if row["formato"] == "multiple_choice":
            if row["respuesta_correcta"] != "A" or "no representa una elección" not in row["justificacion"]:
                raise RuntimeError("MC abstention marker was not disclosed")
        else:
            fields = ["respuesta", "referencia_legal"] if row["formato"] == "semi_open" else ["marco_normativo", "analisis", "jurisprudencia", "conclusion"]
            if any(row[k] for k in fields):
                raise RuntimeError("Dummy made a free-text legal assertion")
        for p in row["pasajes_recuperados"]:
            source = original_passages[p["passage_id"]]
            if p["texto"] != source["text"] or not source["retrieval_eligible"]:
                raise RuntimeError("Evidence changed or was ineligible")
            for key in ["doc_id", "source_url", "norm_name", "article", "hierarchy_path", "graph_node_ids", "source_sha256"]:
                if p[key] != source[key]:
                    raise RuntimeError(f"Evidence provenance changed: {key}")
            evidence_checks += 1
    tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    (ROOT / "reports/member_b_tests_second.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8")
    if tests.returncode:
        raise RuntimeError("Second-pass test suite failed")
    replay = subprocess.run([sys.executable, str(ROOT / "tools/member_b.py"), "smoke", "--config", first["settings"]["config_path"],
                             "--output-root", str(ROOT / "tmp/member_b_second")], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8", timeout=180, check=True)
    replay_summary = json.loads(replay.stdout)
    second_dir = Path(replay_summary["paths"]["run"])
    second = load(second_dir / "experiment.json")
    if first["fingerprint"] != second["fingerprint"] or (run / "submissions.jsonl").read_bytes() != (second_dir / "submissions.jsonl").read_bytes():
        raise RuntimeError("Fresh-process submission differs")
    def deterministic_trace(path):
        return [{k: v for k, v in row.items() if k not in {"latency_ms", "retrieval_ms"}} for row in rows(path)]
    if deterministic_trace(run / "trace.jsonl") != deterministic_trace(second_dir / "trace.jsonl"):
        raise RuntimeError("Routing/evidence/guard trace differs")
    if first["official_evaluation"] != second["official_evaluation"]:
        raise RuntimeError("Official evaluation differs on replay")
    if first["neural_modules_loaded"] or second["neural_modules_loaded"]:
        raise RuntimeError("Model libraries were loaded")
    result = {"ok": True, "timestamp": datetime.now(timezone.utc).isoformat(), "first_run": str(run.resolve()),
              "replay_run": str(second_dir), "official_hashes_unchanged": len(official), "member_a_files_unchanged": unchanged,
              "member_a_model_locks_unchanged": len(original_locks),
              "rows_validated_independently": len(submissions), "evidence_records_verified_against_corpus": evidence_checks,
              "byte_identical_submissions": True, "deterministic_traces_equal": True, "official_evaluation_equal": True,
              "no_neural_modules_loaded": True, "full_test_suite_passed": True,
              "submission_sha256": sha(run / "submissions.jsonl"), "fingerprint": first["fingerprint"],
              "metrics": first["metrics"], "official_total": first["official_evaluation"]["total_automatico"]}
    (ROOT / "reports/member_b_second_verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"member_a_files_unchanged", "metrics"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
