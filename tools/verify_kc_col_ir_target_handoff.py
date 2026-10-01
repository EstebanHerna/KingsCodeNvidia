"""Verify target-machine evidence before unlocking KC-COL-IR C0-C3.

This records an ignored runtime report; it never edits the frozen benchmark manifest.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, file_hash, read_json, write_json
from tools import independent_ir_v2 as benchmark

BENCH = ROOT / "benchmarks/kc_col_ir_v0.1"
DEFAULT_OUTPUT = ROOT / "reports/kc_col_ir_v0.1/target_handoff.json"
EXPECTED = {
    "Qwen/Qwen3-Embedding-0.6B": "97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3",
    "Qwen/Qwen3-Reranker-0.6B": "e61197ed45024b0ed8a2d74b80b4d909f1255473",
    "Qwen/Qwen3-8B": "b968826d9c46dd6066d109eabc6255188de91218",
}


def verify(diagnostic_path: Path, smoke_path: Path, token_audit_path: Path) -> dict:
    diagnostic_path = diagnostic_path.resolve()
    smoke_path = smoke_path.resolve()
    token_audit_path = token_audit_path.resolve()
    diagnostic, smoke, audit = (read_json(p) for p in (diagnostic_path, smoke_path, token_audit_path))
    manifest = read_json(BENCH / "manifest.json")
    sample = read_json(BENCH / "sampling_manifest.json")
    required_pool = ROOT / "tmp/kc_col_ir_v0.1/pool/jep_cuj_2026_full_pool.jsonl"
    if file_hash(required_pool) != sample["pool_artifact_sha256"]:
        raise ValueError("Frozen official question pool missing or hash mismatch")
    archive_path = ROOT / "tmp/kc_col_ir_v0.1/raw/jep-primary/expediente_concurso_jep_2026.zip"
    ledger_path = ROOT / "tmp/kc_col_ir_v0.1/raw/jep-primary/expediente_2026_acquisition.json"
    archive_sha = "3f9dc1765e8ea18588c13a48e1785b506f6a0c06eef3743057e2d34097d9b101"
    acquisition = read_json(ledger_path)
    if file_hash(archive_path) != archive_sha or acquisition.get("archive", {}).get("sha256") != archive_sha:
        raise ValueError("Official CUJ 2026 archive or acquisition ledger identity mismatch")
    if acquisition.get("member_count") != 18 or len(acquisition.get("members", [])) != 18:
        raise ValueError("Official CUJ 2026 acquisition ledger is incomplete")

    torch_info = diagnostic.get("torch", {})
    gpus = diagnostic.get("gpus", [])
    devices = torch_info.get("devices", [])
    if torch_info.get("cuda_available") is not True or torch_info.get("bf16_supported") is not True:
        raise ValueError("Target diagnostic must confirm CUDA and BF16")
    if not any("4090" in str(g.get("name", "")) for g in gpus + devices):
        raise ValueError("Target diagnostic does not identify an RTX 4090")

    if smoke.get("status") != "passed" or smoke.get("model") != "qwen3-8b":
        raise ValueError("Qwen3-8B GPU smoke must pass on the target machine")
    if "4090" not in str(smoke.get("runtime", {}).get("gpu", "")):
        raise ValueError("GPU smoke was not executed on an RTX 4090")
    stages = {row.get("stage") for row in smoke.get("stages", [])}
    if not {"bf16_matmul", "embedding", "reranker", "decoder_and_guards"} <= stages:
        raise ValueError("GPU smoke is missing a required real-runtime stage")
    assets = {row.get("repo_id"): row for row in smoke.get("assets", []) if isinstance(row, dict)}
    if any(assets.get(repo, {}).get("revision") != revision for repo, revision in EXPECTED.items()):
        raise ValueError("GPU smoke does not prove all three frozen model revisions")

    if audit.get("status") != "PASS":
        raise ValueError("Pinned-tokenizer audit must have status PASS")
    audit_identity = audit.get("identity", {})
    if audit_identity.get("benchmark_manifest_sha256") != file_hash(BENCH / "manifest.json"):
        raise ValueError("Token audit belongs to a different benchmark manifest")
    if audit_identity.get("question_manifest_sha256") != file_hash(BENCH / "questions/dev.jsonl"):
        raise ValueError("Token audit question manifest mismatch")
    if audit_identity.get("gold_sha256") != file_hash(BENCH / "gold/dev.jsonl"):
        raise ValueError("Token audit gold mismatch")
    profile_path = BENCH / "review/controlled_cuj2026_v1_profile.json"
    passage_path = ROOT / "tmp/kc_col_ir_v0.1/controlled_cuj2026_v1/passages.jsonl"
    if audit_identity.get("controlled_profile_sha256") != file_hash(profile_path):
        raise ValueError("Token audit controlled profile mismatch")
    if audit_identity.get("controlled_passages_sha256") != file_hash(passage_path):
        raise ValueError("Token audit controlled corpus mismatch")
    for repo, revision in EXPECTED.items():
        if audit_identity.get("encoder", {}).get("revision") != revision and repo.endswith("Embedding-0.6B"):
            raise ValueError("Token audit encoder revision mismatch")
        if audit_identity.get("reranker", {}).get("revision") != revision and repo.endswith("Reranker-0.6B"):
            raise ValueError("Token audit reranker revision mismatch")

    gold = benchmark.read_jsonl(BENCH / "gold/dev.jsonl")
    benchmark.verify_controlled_profile_files(gold)
    inputs = {}
    for name, path in (("diagnostic", diagnostic_path), ("gpu_smoke", smoke_path), ("token_audit", token_audit_path),
                       ("official_archive", archive_path), ("acquisition_ledger", ledger_path)):
        inputs[name] = {"path": str(path), "sha256": file_hash(path)}
    return {
        "status": "PASS",
        "handoff": "KC-COL-IR-v0.1 target runtime",
        "target": "NVIDIA RTX 4090",
        "cuda_available": True,
        "bf16_supported": True,
        "benchmark_manifest_sha256": file_hash(BENCH / "manifest.json"),
        "question_manifest_sha256": file_hash(BENCH / "questions/dev.jsonl"),
        "gold_sha256": file_hash(BENCH / "gold/dev.jsonl"),
        "question_pool_sha256": file_hash(required_pool),
        "controlled_passages_sha256": file_hash(passage_path),
        "models": EXPECTED,
        "inputs": inputs,
        "retrieval_executed": False,
    }


def verify_saved_handoff(path: Path) -> dict:
    report = read_json(path)
    if report.get("status") != "PASS" or report.get("retrieval_executed") is not False:
        raise PermissionError("Target handoff report is not a verified pre-retrieval PASS")
    manifest = read_json(BENCH / "manifest.json")
    for field, target in (("benchmark_manifest_sha256", BENCH / "manifest.json"),
                          ("question_manifest_sha256", BENCH / "questions/dev.jsonl"),
                          ("gold_sha256", BENCH / "gold/dev.jsonl"),
                          ("question_pool_sha256", ROOT / "tmp/kc_col_ir_v0.1/pool/jep_cuj_2026_full_pool.jsonl"),
                          ("controlled_passages_sha256", ROOT / "tmp/kc_col_ir_v0.1/controlled_cuj2026_v1/passages.jsonl")):
        if report.get(field) != file_hash(target):
            raise ValueError(f"Target handoff identity mismatch: {field}")
    for identity in report.get("inputs", {}).values():
        source = Path(identity["path"])
        if not source.is_file() or file_hash(source) != identity.get("sha256"):
            raise ValueError("Target handoff evidence file missing or changed")
    evidence_paths = report.get("inputs", {})
    if set(evidence_paths) != {"diagnostic", "gpu_smoke", "token_audit", "official_archive", "acquisition_ledger"}:
        raise ValueError("Target handoff does not reference the complete evidence set")
    rebuilt = verify(*(Path(evidence_paths[name]["path"]) for name in ("diagnostic", "gpu_smoke", "token_audit")))
    if report != rebuilt:
        raise ValueError("Target handoff report differs from its source evidence")
    if manifest.get("baseline_gate", {}).get("unlocked") is not True:
        raise PermissionError("Frozen ranking baseline gate is locked")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnostic", type=Path, required=True)
    parser.add_argument("--gpu-smoke", type=Path, required=True)
    parser.add_argument("--token-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = verify(args.diagnostic, args.gpu_smoke, args.token_audit)
    write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
