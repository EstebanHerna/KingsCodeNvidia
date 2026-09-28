"""Download only official legal documents; preserve bytes, HTTP evidence and failures.

Uses curl with certificate verification (Schannel on Windows). No LLM, sample
questions, answer keys, or search snippets enter the corpus. Search results only
resolve document URLs and are kept outside raw document input.
"""
from __future__ import annotations

import concurrent.futures
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import urlencode, urljoin, urlparse

from bs4 import BeautifulSoup

from .common import ROOT, digest, normalize, read_json, slug, write_json

FP = "https://www.funcionpublica.gov.co"
ALLOWED_HOSTS = {"www.funcionpublica.gov.co", "www1.funcionpublica.gov.co",
                 "www.corteconstitucional.gov.co", "www.secretariasenado.gov.co",
                 "www.suin-juriscol.gov.co", "www.comunidadandina.org",
                 "www.alcaldiabogota.gov.co", "www.secretariajuridica.gov.co"}
ALLOWED_HOSTS.add("normograma.sena.edu.co")
ALLOWED_HOSTS.update({"cortesuprema.gov.co", "www.cortesuprema.gov.co"})

# Official pages independently resolved before ingest. Other targets use the
# institution's own search catalogue, then validate the downloaded title.
OVERRIDES = {
    "constitucion": (4125, "Constitución Política de Colombia de 1991", "constitution", None, 1991),
    "codigo_general_proceso": (48425, "Código General del Proceso (Ley 1564 de 2012)", "code", "1564", 2012),
    "codigo_sustantivo_trabajo": (199983, "Código Sustantivo del Trabajo (Decreto 2663 de 1950)", "code", "2663", 1950),
    "estatuto_tributario": (6533, "Estatuto Tributario (Decreto 624 de 1989)", "code", "624", 1989),
    "codigo_comercio": (41102, "Código de Comercio (Decreto 410 de 1971)", "code", "410", 1971),
    "codigo_penal": (6388, "Código Penal (Ley 599 de 2000)", "code", "599", 2000),
}


def fetch(url: str, target: Path) -> dict:
    if urlparse(url).scheme != "https" or urlparse(url).hostname not in ALLOWED_HOSTS:
        raise ValueError("Source is not in the official HTTPS allowlist")
    target.parent.mkdir(parents=True, exist_ok=True)
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise RuntimeError("curl required (TLS certificate verification remains enabled)")
    # Redirects are followed manually so every hop is checked before requesting.
    requested = url
    for _ in range(5):
        with tempfile.TemporaryDirectory(prefix="kingscode-http-") as td:
            body, headers = Path(td) / "body", Path(td) / "headers"
            p = subprocess.run([curl, "--silent", "--show-error", "--connect-timeout", "10",
                                "--max-time", "45", "--retry", "1", "--proto", "=https",
                                "--user-agent", "KingsCode-Corpus/0.1 (academic legal retrieval)",
                                "--dump-header", str(headers), "--output", str(body),
                                "--write-out", "%{http_code}", url],
                               capture_output=True, timeout=100, check=False)
            if p.returncode:
                raise RuntimeError(p.stderr.decode("utf-8", errors="replace")[:400])
            status = int(p.stdout.decode().strip()[-3:])
            h = headers.read_text(encoding="latin-1")
            if status in {301, 302, 303, 307, 308}:
                loc = re.findall(r"(?im)^location:\s*(.+)$", h)
                if not loc:
                    raise ValueError("Redirect without location")
                url = urljoin(url, loc[-1].strip())
                if urlparse(url).scheme != "https" or urlparse(url).hostname not in ALLOWED_HOSTS:
                    raise ValueError("Redirect outside official HTTPS allowlist")
                continue
            if status != 200:
                raise ValueError(f"HTTP {status}: {url}")
            data = body.read_bytes()
            if len(data) < 500 or len(data) > 35_000_000:
                raise ValueError(f"Unexpected response size: {len(data)}")
            ctype = re.findall(r"(?im)^content-type:\s*(.+)$", h)
            if not ctype or not any(c in ctype[-1].lower() for c in ["html", "application/pdf"]):
                raise ValueError("Expected an official HTML or PDF document")
            if target.suffix == ".pdf" and not data.startswith(b"%PDF-"):
                raise ValueError("Invalid PDF signature")
            target.write_bytes(data)
            return {"requested_url": requested, "source_url": url, "http_status": status,
                    "content_type": ctype[-1].strip(), "bytes": len(data),
                    "source_sha256": digest(data), "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "tls_verified": True}
    raise ValueError("Too many redirects")


def soup_from_bytes(data: bytes) -> BeautifulSoup:
    # FP declares UTF-8 in HTTP; automatic charset guessing incorrectly picks
    # windows-1252 on its HTML. Decode strict UTF-8 first, then legacy pages.
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Undefined C1 bytes occur in legacy Word HTML from the Court. Latin-1
        # preserves them byte-for-codepoint instead of silently deleting text.
        text = data.decode("windows-1252", errors="surrogateescape")
        text = "".join(chr(ord(c) - 0xDC00) if 0xDC80 <= ord(c) <= 0xDCFF else c for c in text)
    return BeautifulSoup(text, "html.parser")


def make_targets() -> list[dict]:
    seeds = read_json(ROOT / "data/seed_targets.json")["documentos"]
    targets = []
    for s in seeds:
        kind, number, year = s["canonico"]
        t = {"doc_id": slug(s["norma"]), "norm_name": s["norma"],
             "canonical_body": s["canonico"], "areas": s["areas"],
             "priority": s["items_del_banco"], "seed_url": s["donde_buscar"],
             "source_type": {"ley": "law", "decreto": "decree", "jurisprudencia": "decision"}.get(kind, "code"),
             "norm_number": number, "year": int(year) if year else None}
        if kind in OVERRIDES:
            ident, name, st, number, year = OVERRIDES[kind]
            t.update(url=f"{FP}/eva/gestornormativo/norma.php?i={ident}", norm_name=name,
                     source_type=st, norm_number=number, year=year)
        targets.append(t)
    # The seed inventory may omit foundational codes even when they cover an area.
    present = {tuple(x["canonical_body"]) for x in targets}
    for key, (ident, name, st, number, year) in OVERRIDES.items():
        if (key, None, None) not in present:
            targets.append({"doc_id": key, "canonical_body": [key, None, None], "norm_name": name,
                            "source_type": st, "norm_number": number, "year": year,
                            "areas": [], "priority": 0, "url": f"{FP}/eva/gestornormativo/norma.php?i={ident}"})
    return sorted(targets, key=lambda t: (-t["priority"], t["doc_id"]))


def discover(t: dict, cache: Path) -> str:
    if t.get("url"):
        return t["url"]
    kind, number, year = t.get("resolve_as", t["canonical_body"])
    if kind not in {"ley", "decreto", "jurisprudencia", "acto_legislativo"}:
        raise ValueError("Needs manually verified official URL for named code/instrument")
    if kind == "jurisprudencia":
        sala, num = number.split("-", 1)
        if sala in {"C", "T", "SU"}:
            sep = "" if sala == "SU" else "-"
            return f"https://www.corteconstitucional.gov.co/relatoria/{year}/{sala}{sep}{int(num):03d}-{year[-2:]}.htm"
        raise ValueError("Needs verified Corte Suprema/Consejo de Estado URL")
    params = {"find": "FindNext", "filtroNumero": number, "filtroAnio": year,
              "filtroTipoDocumento": {"ley": "Ley", "decreto": "Decreto", "acto_legislativo": "Acto Legislativo"}[kind]}
    search_path = cache / f"{t['doc_id']}.html"
    if not search_path.exists():
        fetch(FP + "/dafpIndexerBGN/norma/index?" + urlencode(params), search_path)
    soup = soup_from_bytes(search_path.read_bytes())
    for a in soup.find_all("a", href=True):
        label = normalize(a.get_text(" ", strip=True))
        if "norma.php" in a["href"] and re.search(rf"\b{number}\s+de\s+{year}\b", label):
            return urljoin(FP, a["href"])
    raise ValueError("No exact document found in official catalogue")


def acquire_one(t: dict, out: Path) -> dict:
    suffix = ".pdf" if t.get("url", "").lower().endswith(".pdf") else ".html"
    raw = out / "raw" / f"{t['doc_id']}{suffix}"
    meta = raw.with_suffix(".meta.json")
    try:
        if raw.exists() and meta.exists():
            record = read_json(meta)
            if digest(raw.read_bytes()) != record["source_sha256"]:
                raise ValueError("Cached raw checksum mismatch")
            if record.get("status") == "downloaded":
                return {**t, **record}
        url = discover(t, out / "discovery")
        record = fetch(url, raw)
        if suffix == ".pdf":
            import io
            import pdfplumber
            with pdfplumber.open(io.BytesIO(raw.read_bytes())) as pdf:
                text = " ".join((p.extract_text() or "") for p in pdf.pages[:2])
                identity = t.get("pdf_identity")
                if not identity or not re.search(identity, text, re.I):
                    raise ValueError("PDF identity mismatch")
                record["pdf_pages"] = len(pdf.pages)
            record.update(status="downloaded", raw_path=raw.relative_to(ROOT).as_posix(), source_title=t["norm_name"])
            write_json(meta, {**t, **record})
            return {**t, **record}
        soup = soup_from_bytes(raw.read_bytes())
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        body = soup.select_one(".descripcion-contenido")
        if "funcionpublica.gov.co" in urlparse(record["source_url"]).hostname:
            if body is None or len(body.get_text(strip=True)) < 150:
                raise ValueError("Official document body not present (error/search page)")
            identity = normalize(title + " " + body.get_text(" ", strip=True)[:1000])
            if t["norm_number"] and not re.search(rf"\b{t['norm_number']}\s+de\s+{t['year']}\b", identity):
                raise ValueError("Source identity mismatch")
            if t["canonical_body"][0] == "constitucion" and "1991" not in identity:
                raise ValueError("Constitution identity mismatch")
        elif "normograma.sena.edu.co" in url:
            body = soup.select_one(".panel-documento")
            if body is None or not re.search(r"LEY\s+84\s+DE\s+1873", body.get_text(" ", strip=True)[:1000], re.I):
                raise ValueError("SENA Civil Code identity mismatch")
        else:
            kind, number, year = t["canonical_body"]
            text = normalize(soup.get_text(" ", strip=True))
            sala, num = number.split("-", 1)
            if not re.search(rf"\b{sala.lower()}\s*[- ]?\s*0*{int(num)}\s*[/ -]\s*(?:{year}|{year[-2:]})\b", text[:20000]):
                raise ValueError("Decision identity not found in downloaded document")
            if len(text) < 4000:
                raise ValueError("Decision response too short")
        record.update(status="downloaded", raw_path=raw.relative_to(ROOT).as_posix(), source_title=title)
        write_json(meta, {**t, **record})
        return {**t, **record}
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        return {**t, "status": "failed", "error": str(exc)[:500]}


def acquire(out: Path, limit: int | None = None, workers: int = 3) -> dict:
    targets_path = ROOT / "config/sources.json"
    targets = read_json(targets_path) if targets_path.exists() else make_targets()
    if not targets_path.exists():
        write_json(targets_path, targets)
    chosen = targets[:limit] if limit else targets
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda t: acquire_one(t, out), chosen))
    report = {"targets": len(chosen), "downloaded": sum(r["status"] == "downloaded" for r in results),
              "documents": results}
    write_json(out / "acquisition.json", report)
    return report
