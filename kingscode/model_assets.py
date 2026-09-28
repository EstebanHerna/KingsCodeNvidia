"""Immutable model resolution and verified, offline Hugging Face snapshots.

No torch/transformers imports and no downloads at import time.
"""
from __future__ import annotations

import fnmatch
import hashlib
from pathlib import Path
import re

from .common import ROOT, read_json, write_json

RETRIEVAL = ("Qwen/Qwen3-Embedding-0.6B", "Qwen/Qwen3-Reranker-0.6B")
DECODERS = ("Qwen/Qwen3-8B", "SINAI/ALIA-es-legal-administrative-7B-Instruct",
            "BSC-LT/salamandra-7b-fc-2607", "meta-llama/Llama-3.1-8B-Instruct")
PATTERNS = ["*.json", "*.safetensors", "*.txt", "*.model", "*.jinja", "README.md", "LICENSE", "USE_POLICY.md"]


def resolve_model(name: str, lock_path: Path = ROOT / "config/models.lock.json") -> dict:
    lock = read_json(lock_path)
    matches = [entry for repo, entry in lock.items() if name in (repo, entry.get("alias"))]
    if len(matches) != 1:
        raise ValueError(f"Unknown/ambiguous locked model: {name}")
    entry = dict(matches[0])
    if entry.get("repo_id") not in RETRIEVAL + DECODERS:
        raise ValueError("Model is not an approved open candidate")
    if not re.fullmatch(r"[0-9a-f]{40}", entry.get("revision", "")):
        raise ValueError("Missing immutable 40-character model revision")
    if not entry.get("license"):
        raise ValueError("Missing verified license")
    return entry


def digest_file(path: Path, *, git_blob: bool = False) -> str:
    digest = hashlib.sha1() if git_blob else hashlib.sha256()
    if git_blob:
        digest.update(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_path(entry: dict, cache_dir: Path) -> Path:
    return cache_dir / ".kingscode_manifests" / f"{entry['repo_id'].replace('/', '--')}-{entry['revision']}.json"


def snapshot_path(entry: dict, cache_dir: Path) -> Path:
    return cache_dir / ("models--" + entry["repo_id"].replace("/", "--")) / "snapshots" / entry["revision"]


def _contained_file(snapshot: Path, name: str) -> Path:
    # Hub files may be symlinks into the sibling blobs directory; validate the
    # logical relative name, not symlink resolution outside the snapshot folder.
    if Path(name).is_absolute() or ".." in Path(name).parts or "\\" in name or ":" in name:
        raise ValueError("Unsafe snapshot filename")
    return snapshot / name


def _required_files(snapshot: Path, names: set[str]):
    if not {"config.json", "tokenizer_config.json"} <= names:
        raise ValueError("Incomplete model configuration/tokenizer")
    if not ({"tokenizer.json", "tokenizer.model", "vocab.json"} & names):
        raise ValueError("Missing tokenizer vocabulary")
    index = snapshot / "model.safetensors.index.json"
    if index.is_file():
        shards = set(read_json(index).get("weight_map", {}).values())
        if not shards or not shards <= names:
            raise ValueError("Missing safetensors shards")
    elif "model.safetensors" not in names:
        raise ValueError("Missing safetensors weights; pickle weights are not accepted")


def verify_snapshot(entry: dict, cache_dir: Path = ROOT / "models") -> dict:
    """Offline verification against hashes authenticated during preparation."""
    path = manifest_path(entry, cache_dir)
    if not path.is_file():
        raise FileNotFoundError(f"MODEL_NOT_PREPARED: run tools/prepare_models.py --download {entry.get('alias', entry['repo_id'])}")
    manifest = read_json(path)
    if manifest.get("repo_id") != entry["repo_id"] or manifest.get("revision") != entry["revision"]:
        raise ValueError("Prepared model revision mismatch")
    snapshot = snapshot_path(entry, cache_dir)
    files = manifest["files"]
    _required_files(snapshot, set(files))
    actual = {p.relative_to(snapshot).as_posix() for p in snapshot.rglob("*") if p.is_file()}
    if actual != set(files):
        raise ValueError("Snapshot file inventory changed")
    for name, metadata in files.items():
        p = _contained_file(snapshot, name)
        if not p.is_file() or p.stat().st_size != metadata["size"] or digest_file(p) != metadata["sha256"]:
            raise ValueError(f"Model file hash mismatch: {name}")
    return {"repo_id": entry["repo_id"], "revision": entry["revision"], "snapshot": str(snapshot.resolve()),
            "manifest": str(path.resolve()), "manifest_sha256": digest_file(path), "files_verified": len(files)}


def prepare_snapshot(entry: dict, cache_dir: Path = ROOT / "models", *, api=None, download=None) -> dict:
    """Explicit network action. Compare every file with Hub Git/LFS metadata."""
    if api is None or download is None:
        from huggingface_hub import HfApi, snapshot_download
        api, download = api or HfApi(), download or snapshot_download
    info = api.model_info(entry["repo_id"], revision=entry["revision"], files_metadata=True)
    if info.sha != entry["revision"]:
        raise ValueError("Hub returned a different revision")
    snapshot = Path(download(entry["repo_id"], revision=entry["revision"], cache_dir=str(cache_dir),
                             allow_patterns=PATTERNS, local_files_only=False))
    if snapshot.absolute() != snapshot_path(entry, cache_dir).absolute():
        raise ValueError("Download is not the requested cache snapshot")
    files = {}
    for sibling in info.siblings:
        name = sibling.rfilename
        if not any(fnmatch.fnmatch(name, pattern) for pattern in PATTERNS):
            continue
        p = _contained_file(snapshot, name)
        if not p.is_file():
            raise ValueError(f"Incomplete download: {name}")
        sha256 = digest_file(p)
        lfs = sibling.lfs
        expected = (lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)) if lfs else sibling.blob_id
        actual = sha256 if lfs else digest_file(p, git_blob=True)
        if not expected or actual != expected:
            raise ValueError(f"Hub integrity check failed: {name}")
        files[name] = {"size": p.stat().st_size, "sha256": sha256,
                       "hub_hash": expected, "hub_hash_kind": "sha256" if lfs else "git_blob_sha1"}
    _required_files(snapshot, set(files))
    write_json(manifest_path(entry, cache_dir), {"repo_id": entry["repo_id"], "revision": info.sha,
                                               "license": entry["license"], "files": files})
    return verify_snapshot(entry, cache_dir)
