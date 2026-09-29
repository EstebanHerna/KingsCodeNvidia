"""Build a local, separately scoped corpus from every textual PDF in the CUJ 2026 ZIP.

Raw source and extracted passage text remain ignored under tmp/. The committed
profile artifacts contain hashes, identities, locators and passage IDs only.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_ID = "KC-COL-IR-CUJ2026-CONTROLLED-v1"
ARCHIVE = ROOT / "tmp/kc_col_ir_v0.1/raw/jep-primary/expediente_concurso_jep_2026.zip"
ACQUISITION = ROOT / "tmp/kc_col_ir_v0.1/raw/jep-primary/expediente_2026_acquisition.json"
OUT = ROOT / "tmp/kc_col_ir_v0.1/controlled_cuj2026_v1"
PROFILE_DIR = ROOT / "benchmarks/kc_col_ir_v0.1/review"
SOURCE_URL = "https://concursouniversitariorelatoria.jep.gov.co/concursocarp/expedientes/EXPEDIENTE_CONCURSO_JEP_2026.zip"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(obj: object) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
                    encoding="utf-8", newline="\n")


def inventory_kind(name: str, data: bytes, is_dir: bool) -> str:
    if is_dir:
        return "DIRECTORY_METADATA"
    if name.startswith("__MACOSX/") or "/._" in name or name.rsplit("/", 1)[-1].startswith("._"):
        return "ARCHIVE_METADATA"
    if name.lower().endswith(".pdf") and data.startswith(b"%PDF-"):
        return "TEXTUAL_PDF_CANDIDATE"
    if name.lower().endswith(".mp3"):
        return "AUDIO"
    return "UNSUPPORTED_BINARY"


def build(archive: Path = ARCHIVE, output: Path = OUT, profile_dir: Path = PROFILE_DIR,
          materialize: bool = True) -> dict:
    try:
        from pypdf import PdfReader, __version__ as pypdf_version
    except ImportError as exc:
        raise RuntimeError("Build requires pypdf; use the pinned workspace Python runtime") from exc

    acquisition = json.loads(ACQUISITION.read_text(encoding="utf-8"))
    archive_sha = digest(archive.read_bytes())
    expected_archive = "3f9dc1765e8ea18588c13a48e1785b506f6a0c06eef3743057e2d34097d9b101"
    if archive_sha != expected_archive or acquisition.get("member_count") != 18:
        raise ValueError("Official CUJ 2026 archive identity/count mismatch")

    raw_members: list[dict] = []
    documents: list[dict] = []
    passages: list[dict] = []
    with zipfile.ZipFile(archive) as zf:
        if len(zf.infolist()) != 18 or zf.testzip() is not None:
            raise ValueError("Official archive CRC/member-count check failed")
        for index, info in enumerate(zf.infolist(), 1):
            data = zf.read(info)
            member_path = acquisition["members"][index - 1]["archive_member_name_utf8_recovered"]
            if acquisition["members"][index - 1]["sha256"] != digest(data):
                raise ValueError(f"Archive member differs from preserved acquisition ledger: {index}")
            member_sha = digest(data)
            kind = inventory_kind(member_path, data, info.is_dir())
            member_meta = {
                "member_index": index,
                "member_path": member_path,
                "classification": kind,
                "uncompressed_bytes": len(data),
                "member_sha256": member_sha,
                "archive_sha256": archive_sha,
                "source_url": SOURCE_URL,
                "ingested": False,
            }
            if kind == "TEXTUAL_PDF_CANDIDATE":
                reader = PdfReader(io.BytesIO(data), strict=False)
                page_texts = [page.extract_text() or "" for page in reader.pages]
                if not any(text.strip() for text in page_texts):
                    raise ValueError(f"PDF contains no extractable text: member {index}")
                doc_id = f"CUJ2026-D{index:02d}-{member_sha[:12]}"
                title = member_path.rsplit("/", 1)[-1]
                page_ids: list[str] = []
                for page_no, text in enumerate(page_texts, 1):
                    if not text.strip():
                        continue
                    passage_id = f"CUJ2026-P{index:02d}-{page_no:04d}-{member_sha[:12]}"
                    page_ids.append(passage_id)
                    passages.append({
                        "passage_id": passage_id,
                        "doc_id": doc_id,
                        "canonical_document_id": doc_id,
                        "text": text,
                        "norm_name": title,
                        "article": None,
                        "source_url": SOURCE_URL,
                        "hierarchy_path": [title, f"PDF page {page_no}"],
                        "graph_node_ids": [],
                        "source_page": page_no,
                        "source_archive_sha256": archive_sha,
                        "source_member_path": member_path,
                        "source_member_sha256": member_sha,
                        "char_start": 0,
                        "char_end": len(text),
                        "offset_unit": "unicode_codepoint_within_pdf_page_text",
                        "parser_version": f"pypdf-{pypdf_version}-page-extract-text",
                        "is_current_text": True,
                        "retrieval_eligible": True,
                    })
                member_meta.update({"ingested": True, "doc_id": doc_id,
                                    "page_count": len(page_texts), "passage_ids": page_ids,
                                    "parser_version": f"pypdf-{pypdf_version}-page-extract-text"})
                documents.append({
                    "doc_id": doc_id,
                    "member_index": index,
                    "member_path": member_path,
                    "document_identity": title,
                    "source_url": SOURCE_URL,
                    "source_archive_sha256": archive_sha,
                    "source_member_sha256": member_sha,
                    "source_member_bytes": len(data),
                    "parser_version": f"pypdf-{pypdf_version}-page-extract-text",
                    "page_count": len(page_texts),
                    "passage_count": len(page_ids),
                    "passage_ids": page_ids,
                })
            raw_members.append(member_meta)

    if len(documents) != 6:
        raise ValueError(f"Expected all six eligible textual PDFs; found {len(documents)}")
    sys.path.insert(0, str(ROOT))
    from kingscode.retrieval import BM25Index
    from kingscode.common import indexable
    passage_bytes = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in passages).encode("utf-8")
    corpus_sha = digest(passage_bytes)
    bm25 = BM25Index([p for p in passages if indexable(p)])
    if materialize:
        output.mkdir(parents=True, exist_ok=True)
        write_jsonl(output / "passages.jsonl", passages)
        write_jsonl(output / "graph/nodes.jsonl", [])
        write_jsonl(output / "graph/edges.jsonl", [])
        bm25.save(output / "index/bm25.json", corpus_sha)
    build_identity = {
        "profile_id": PROFILE_ID,
        "source_archive_sha256": archive_sha,
        "pypdf_version": pypdf_version,
        "parser_rule": "extract_text once per physical PDF page; preserve returned Unicode text; page is the passage boundary",
        "documents": [{k: d[k] for k in ("doc_id", "member_index", "source_member_sha256", "page_count", "passage_count")} for d in documents],
        "passages_sha256": corpus_sha,
        "passage_count": len(passages),
    }
    build_sha = digest(canonical_bytes(build_identity))
    runtime_manifest = {
        **build_identity,
        "build_sha256": build_sha,
        "corpus_root": str(output.relative_to(ROOT).as_posix()),
        "index_files": {"passages.jsonl": corpus_sha},
        "redistribution": "Local ignored build only; source and extracted text are not committed pending rights review.",
        "materialized": materialize,
    }
    if materialize:
        runtime_manifest["index_files"].update({
            "index/bm25.json": digest((output / "index/bm25.json").read_bytes()),
            "graph/nodes.jsonl": digest((output / "graph/nodes.jsonl").read_bytes()),
            "graph/edges.jsonl": digest((output / "graph/edges.jsonl").read_bytes()),
        })
        write_json(output / "manifest.json", runtime_manifest)
        profile_dir.mkdir(parents=True, exist_ok=True)
        write_json(profile_dir / "controlled_cuj2026_v1_profile.json", {
        "profile_id": PROFILE_ID,
        "purpose": "Controlled retrieval ranking corpus, separate from competitive corpus-v0.1",
        "source_boundary": "All eligible textual PDF members of the complete official CUJ 2026 expediente ZIP; no gold-driven document selection",
        "source_archive_sha256": archive_sha,
        "build_sha256": build_sha,
        "passages_sha256": corpus_sha,
        "document_count": len(documents),
        "passage_count": len(passages),
        "page_count": sum(d["page_count"] for d in documents),
        "parser": f"pypdf-{pypdf_version}-page-extract-text",
        "local_corpus_root": "ignored:tmp/kc_col_ir_v0.1/controlled_cuj2026_v1",
        "materialized": True,
        "index_files": runtime_manifest["index_files"],
        "audio_policy": "Audio members inventoried but excluded from text passages; no ASR/generative transcription.",
        "redistribution": "Derived page text remains ignored/local pending rights review.",
        "retrieval_executed": False,
        })
        write_jsonl(profile_dir / "controlled_cuj2026_v1_source_inventory.jsonl", raw_members)
        write_jsonl(profile_dir / "controlled_cuj2026_v1_documents.jsonl", documents)
    return {"status": "PASS", "profile_id": PROFILE_ID, "archive_sha256": archive_sha,
            "archive_members": len(raw_members), "documents": len(documents),
            "pages": sum(d["page_count"] for d in documents), "passages": len(passages),
            "passages_sha256": corpus_sha, "build_sha256": build_sha,
            "parser": f"pypdf-{pypdf_version}-page-extract-text", "materialized": materialize}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--profile-dir", type=Path, default=PROFILE_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Verify inventory and hashes without writing files")
    args = parser.parse_args()
    print(json.dumps(build(args.archive, args.output, args.profile_dir, materialize=not args.dry_run),
                       ensure_ascii=False, indent=2))
