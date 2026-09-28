"""Prepared verification for the GPU day. Not executed during Gate 2-Prep delivery.

Both stages use a fresh process for tests and the unchanged dummy smoke. The
second stage independently compares baseline files, hashes and exact output.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = "254fa3a1ecd528137943007ef8946d9662d5bab7"


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=["first", "second"])
    args = parser.parse_args(argv)
    def load(path):
        return json.loads(path.read_text(encoding="utf-8-sig"))
    official_count = 0
    for line in (ROOT / "docs/OFFICIAL_SHA256.txt").read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            expected, path = line.split("  ", 1)
            if digest(ROOT / path) != expected:
                raise RuntimeError(f"Official file changed: {path}")
            official_count += 1
    unchanged = ["config/reasoning.json", "tests/test_knowledge.py", "tests/test_reasoning.py"]
    unchanged += [p.relative_to(ROOT).as_posix() for folder in (ROOT / "kingscode", ROOT / "kingscode/reasoning") for p in folder.glob("*.py")
                  if p.name not in {"model_assets.py", "gpu_environment.py"}]
    for path in unchanged:
        original = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)
        if original != (ROOT / path).read_bytes():
            raise RuntimeError(f"Baseline implementation changed: {path}")
    old_lock = json.loads(subprocess.check_output(["git", "show", f"{BASE}:config/models.lock.json"], cwd=ROOT))
    lock = load(ROOT / "config/models.lock.json")
    if any(lock.get(k) != v for k, v in old_lock.items()):
        raise RuntimeError("Retrieval locks changed")
    corpus = load(ROOT / "corpus/manifest.json")
    for path, expected in corpus["hashes"].items():
        if digest(ROOT / "corpus" / path) != expected:
            raise RuntimeError(f"Corpus hash changed: {path}")
    if digest(ROOT / "corpus/index/bm25.json") != corpus["bm25_sha256"]:
        raise RuntimeError("BM25 changed")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8", env=env, timeout=300)
    report_dir = ROOT / "reports/gate2_prep_verification" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + args.stage)
    report_dir.mkdir(parents=True, exist_ok=False)
    (report_dir / "tests.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8")
    if tests.returncode:
        raise RuntimeError(f"Tests failed; see {report_dir / 'tests.txt'}")
    smoke = subprocess.run([sys.executable, "tools/member_b.py", "smoke", "--output-root", str(ROOT / "tmp/gate2_dummy")],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8", env=env, timeout=180, check=True)
    result = json.loads(smoke.stdout)
    original_run = ROOT / "reports/member_b/20260928T035443616407Z-9a776fef5883"
    original = load(original_run / "experiment.json")
    if (Path(result["paths"]["submission"]).read_bytes() != (original_run / "submissions.jsonl").read_bytes()
            or result["fingerprint"] != original["fingerprint"] or result["neural_modules_loaded"]):
        raise RuntimeError("Gate 1B dummy reproduction changed")
    report = {"status": "passed", "stage": args.stage, "official_files_unchanged": official_count,
              "baseline_files_unchanged": unchanged, "retrieval_locks_unchanged": len(old_lock),
              "tests_passed": True, "dummy_byte_identical": True, "dummy_fingerprint_identical": True,
              "gpu_executed": False, "real_decoder_executed": False, "smoke": result}
    (report_dir / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "report": str(report_dir / "verification.json")}, indent=2))


if __name__ == "__main__":
    main()
