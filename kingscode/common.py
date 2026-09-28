"""Deterministic IO and text utilities shared by the knowledge layer."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "corpus-v0.1"


def normalize(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower())
                   if not unicodedata.combining(c))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_hash(path: Path) -> str:
    return digest(path.read_bytes())


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", normalize(text)).strip("_")


def indexable(passage: dict) -> bool:
    return passage.get("is_current_text") is not False and passage.get("retrieval_eligible", True)
