"""Package the existing corpus-v0.1 bytes for transfer, without acquisition or rebuilding.

    python tools/package_corpus_snapshot.py pack                 # en la PC que tiene corpus/
    python tools/package_corpus_snapshot.py verify <archivo.tar.gz> [--files snapshot-files.sha256.json]

`pack` checks every hash in corpus/manifest.json first, writes a deterministic
tar.gz (sorted names, mtime 0, fixed mode) plus snapshot-files.sha256.json,
SHA256SUMS.txt and LEEME.txt into dist/corpus_snapshot/ (ignored by git), then
re-reads the archive and verifies every member. `verify` checks an archive on the
receiving PC before extracting it. Per-file hashes are the authoritative check:
the archive-level SHA-256 can differ across zlib builds even for identical content.
"""
from pathlib import Path, PurePosixPath
import argparse
import gzip
import hashlib
import json
import tarfile

REPO = Path(__file__).resolve().parents[1]
ARCHIVE_NAME = "kingscode-corpus-v0.1.tar.gz"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def leeme(archive_hash: str, documents, passages) -> str:
    return f"""KingsCode - snapshot historico corpus-v0.1

Archivo: {ARCHIVE_NAME}
SHA-256: {archive_hash}
Contenido: corpus/ completo; {documents} documentos, {passages} pasajes, grafo e indice BM25.
Incluye raw, clean, acquisition.json y manifest.json.
No incluye indice denso (dense.npy), pesos de modelos, pool JEP ni freeze de retrieval.
Es el snapshot historico v0.1; no es un freeze competitivo ni el corpus v0.2.

En la PC que lo recibe (Windows PowerShell), desde la raiz del repositorio actualizado y sin otra carpeta corpus/:
1. Copiar {ARCHIVE_NAME} y snapshot-files.sha256.json.
2. Verificar antes de extraer (autoritativo, archivo por archivo):
   .\\.venv\\Scripts\\python.exe tools\\package_corpus_snapshot.py verify <ruta>\\{ARCHIVE_NAME} --files <ruta>\\snapshot-files.sha256.json
   (Get-FileHash -Algorithm SHA256 solo coincide si se usa la misma build de zlib.)
3. Extraer:  tar -xzf <ruta>\\{ARCHIVE_NAME} -C .
4. Verificar contra el manifest de A:  .\\.venv\\Scripts\\python.exe tools\\verify_member_a_v02.py

Tambien puede pasarse la ruta del .tar.gz a -CorpusSnapshot de tools\\lab_gpu_session.ps1
(el paquete por si solo no instala Python, CUDA ni modelos).
No ejecutar acquire/reproduce para transferir el corpus: cambiaria los hashes.
"""


def pack(root: Path, out: Path) -> dict:
    corpus = root / "corpus"
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    checks = [(corpus / rel, expected) for rel, expected in manifest["hashes"].items()]
    checks.append((corpus / "index/bm25.json", manifest["bm25_sha256"]))
    for doc in manifest["documentos"]:
        checks.extend([(root / doc["raw_path"], doc["source_sha256"]), (root / doc["clean_path"], doc["sha256"])])
    for path, expected in checks:
        if sha(path) != expected:
            raise ValueError(f"Source snapshot hash mismatch: {path}")
    paths = sorted(p for p in corpus.rglob("*") if p.is_file())
    if any(p.is_symlink() for p in paths):
        raise ValueError("Snapshot contains a symlink")
    hashes = {p.relative_to(root).as_posix(): sha(p) for p in paths}
    out.mkdir(parents=True, exist_ok=True)
    archive = out / ARCHIVE_NAME
    if archive.exists():
        raise FileExistsError(archive)
    with archive.open("xb") as output:
        with gzip.GzipFile(filename="", fileobj=output, mode="wb", mtime=0, compresslevel=6) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.PAX_FORMAT) as tar:
                for p in paths:
                    info = tarfile.TarInfo(p.relative_to(root).as_posix())
                    info.size, info.mtime, info.mode = p.stat().st_size, 0, 0o644
                    with p.open("rb") as stream:
                        tar.addfile(info, stream)
    verified = verify(archive, hashes)
    if any(sha(root / name) != expected for name, expected in hashes.items()):
        raise ValueError("Source changed during packaging")
    archive_hash = sha(archive)
    result = {"snapshot": "corpus-v0.1", "competitive_freeze": False, "documents": manifest["n_documentos"],
              "passages": manifest["n_fragmentos"], "index": "BM25 only; dense index and model weights are not included",
              "archive": ARCHIVE_NAME, "archive_bytes": archive.stat().st_size, "archive_sha256": archive_hash,
              "files_verified": verified, "files": hashes}
    (out / "snapshot-files.sha256.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (out / "SHA256SUMS.txt").write_text(f"{archive_hash}  {ARCHIVE_NAME}\n", encoding="utf-8", newline="\n")
    (out / "LEEME.txt").write_text(leeme(archive_hash, manifest["n_documentos"], manifest["n_fragmentos"]), encoding="utf-8", newline="\n")
    return result


def verify(archive: Path, hashes: dict) -> int:
    """Every member must be a safe relative corpus/ file with the expected SHA-256; nothing missing or extra."""
    seen = set()
    with tarfile.open(archive, "r:gz") as tar:
        for item in tar:
            name = PurePosixPath(item.name)
            if not item.isfile() or name.is_absolute() or ".." in name.parts or name.parts[0] != "corpus":
                raise ValueError(f"Unsafe or unexpected archive member: {item.name}")
            with tar.extractfile(item) as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != hashes.get(item.name):
                    raise ValueError(f"Archived bytes differ: {item.name}")
            seen.add(item.name)
    if seen != set(hashes):
        raise ValueError(f"Archive members differ from the expected list ({len(seen)} vs {len(hashes)})")
    return len(seen)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("pack")
    p.add_argument("--root", type=Path, default=REPO)
    p.add_argument("--out", type=Path, default=REPO / "dist/corpus_snapshot")
    v = sub.add_parser("verify")
    v.add_argument("archive", type=Path)
    v.add_argument("--files", type=Path, help="snapshot-files.sha256.json (default: next to the archive)")
    args = ap.parse_args()
    if args.command == "pack":
        result = pack(args.root, args.out)
        print(json.dumps({k: v for k, v in result.items() if k != "files"}, ensure_ascii=False, indent=2))
        return 0
    files = args.files or args.archive.with_name("snapshot-files.sha256.json")
    expected = json.loads(files.read_text(encoding="utf-8"))["files"]
    print(json.dumps({"archive": str(args.archive), "files_verified": verify(args.archive, expected), "status": "PASS"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
