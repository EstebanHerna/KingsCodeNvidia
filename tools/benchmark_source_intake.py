"""Verify externally acquired official benchmark PDFs before local extraction.

Place source files under ``tmp/official-source-intake/`` (ignored by Git), then
provide the SHA-256 received from the independent acquisition environment. This
checks byte integrity and PDF framing; it does not prove legal authenticity or
grant redistribution rights. No question text is emitted or stored.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kingscode.common import ROOT, read_jsonl

INTAKE_RELATIVE = Path("tmp/official-source-intake")
ALLOWED_SOURCE_IDS = {
    "ICFES-GESTION-CONFLICTO-2026",
    "ICFES-COMUNICACION-JURIDICA-2021",
    "ICFES-COMUNICACION-JURIDICA-2026",
    "ICFES-GESTION-CONFLICTO-2018-EXTERNADO",
}
MIRROR_SOURCE_ID = "ICFES-GESTION-CONFLICTO-2018-EXTERNADO"
ICFES_HOSTS = {"www.icfes.gov.co", "icfes.gov.co"}


def verify_pdf(source_id: str, file_path: Path, expected_sha256: str, *, root: Path = ROOT) -> dict:
    """Validate a local official-source candidate and return metadata only."""
    if source_id not in ALLOWED_SOURCE_IDS:
        raise ValueError(f"Source is not enabled for external intake: {source_id}")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256 or ""):
        raise ValueError("Expected SHA-256 must be 64 hexadecimal characters")

    intake_dir = (root / INTAKE_RELATIVE).resolve()
    resolved = file_path.resolve(strict=True)
    try:
        resolved.relative_to(intake_dir)
    except ValueError as exc:
        raise ValueError(f"Input must be placed inside {INTAKE_RELATIVE.as_posix()}") from exc
    if not resolved.is_file() or resolved.suffix.lower() != ".pdf":
        raise ValueError("Intake input must be a regular .pdf file")

    rows = read_jsonl(root / "benchmarks/kingscode_ir_v2/source_manifest.jsonl")
    source = next((row for row in rows if row.get("source_id") == source_id), None)
    if source is None:
        raise ValueError(f"Source is not recorded in the benchmark manifest: {source_id}")
    official_url = source.get("official_listing_url") or source.get("official_url") or source.get("candidate_item_url") or source.get("url")
    if source_id == MIRROR_SOURCE_ID:
        retrieval_url = source.get("retrieval_url")
        allowed_hostname = source.get("retrieval_allowed_hostname")
        if urlparse(official_url or "").hostname not in ICFES_HOSTS:
            raise ValueError("Mirror identity listing is not on the official ICFES domain")
        if source.get("canonical_source_status") != "OFFICIAL_ICFES_LISTING_VERIFIED":
            raise ValueError("Mirror requires a verified official ICFES listing")
        if source.get("retrieval_status", "").startswith("INSTITUTIONAL_MIRROR") is False:
            raise ValueError("Mirror source must retain its institutional-mirror status")
        if not allowed_hostname or urlparse(retrieval_url or "").hostname != allowed_hostname:
            raise ValueError("Mirror retrieval URL does not match its manifest allowlist")
    else:
        retrieval_url = source.get("official_url") or source.get("candidate_item_url") or source.get("url")
        if urlparse(retrieval_url or "").hostname not in ICFES_HOSTS:
            raise ValueError("Manifest source is not on the official ICFES domain")

    digest = hashlib.sha256()
    with resolved.open("rb") as stream:
        header = stream.read(5)
        if header != b"%PDF-":
            raise ValueError("Input does not have a PDF header")
        digest.update(header)
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    if not hmac.compare_digest(actual.lower(), expected_sha256.lower()):
        raise ValueError(f"SHA-256 mismatch: actual={actual}")

    return {
        "status": "HASH_VERIFIED_READY_FOR_LOCAL_EXTRACTION",
        "source_id": source_id,
        "issuer": source.get("issuer") or source.get("institution", "ICFES"),
        "canonical_year": source.get("canonical_year") or source.get("year"),
        "canonical_source_status": source.get("canonical_source_status"),
        "official_url": official_url,
        "retrieval_host": source.get("retrieval_host") or urlparse(retrieval_url).hostname,
        "retrieval_url": retrieval_url,
        "retrieval_status": source.get("retrieval_status"),
        "identity_verification": source.get("identity_verification"),
        "local_path": resolved.relative_to(root.resolve()).as_posix(),
        "bytes": resolved.stat().st_size,
        "sha256": actual,
        "hash_scope": "integrity_only_authenticity_and_use_terms_require_separate_review",
        "question_text_emitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id", required=True, choices=sorted(ALLOWED_SOURCE_IDS))
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    try:
        result = verify_pdf(args.source_id, args.file, args.sha256)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
