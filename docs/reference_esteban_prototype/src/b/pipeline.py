"""Comando unico: preguntas -> submissions.jsonl -> evaluacion -> bitacora.

Ejemplos:
  python -m b.pipeline --split sample                           # mock, prueba del harness
  python -m b.pipeline --split sample --config configs/qwen3.json
  python -m b.pipeline --input oficial/data/test_992.jsonl --config configs/final.json --out submissions.jsonl

Reanuda automaticamente: cada fila terminada se guarda en runs/<tag>/cache.jsonl.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .answer import answer_item
from .config import DATA, RUNS, SCRIPTS, Config
from .contract import load_retriever
from .validate import validate_file

import common  # oficial

FIELDS_IN = ("id", "formato", "area", "tema", "complejidad", "sub_tarea", "pregunta", "opciones")


def load_items(path: Path) -> list[dict]:
    # solo los campos de entrada: nunca se leen respuestas ni legal_basis
    return [{k: r.get(k) for k in FIELDS_IN} for r in common.read_jsonl(path)]


def run(items: list[dict], cfg: Config, out: Path, run_dir: Path) -> list[dict]:
    retrieve = load_retriever(cfg.retriever)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_text(cfg.to_json(), encoding="utf-8")
    cache_p, log_p = run_dir / "cache.jsonl", run_dir / "log.jsonl"
    done = {r["id"]: r for r in common.read_jsonl(cache_p)} if cache_p.exists() else {}
    todo = [it for it in items if it["id"] not in done]
    print(f"[B] {len(done)} en cache, {len(todo)} por responder, concurrencia {cfg.concurrency}", file=sys.stderr)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, cfg.concurrency)) as ex, \
            cache_p.open("a", encoding="utf-8") as fc, log_p.open("a", encoding="utf-8") as fl:
        futs = {ex.submit(answer_item, it, cfg, retrieve): it["id"] for it in todo}
        for n, fu in enumerate(as_completed(futs), 1):
            row, log = fu.result()
            done[row["id"]] = row
            fc.write(json.dumps(row, ensure_ascii=False) + "\n"); fc.flush()
            fl.write(json.dumps(log, ensure_ascii=False) + "\n"); fl.flush()
            if n % 25 == 0 or n == len(todo):
                el = time.time() - t0
                print(f"[B] {n}/{len(todo)}  {el:.0f}s  ~{el / n * (len(todo) - n):.0f}s restantes", file=sys.stderr)
    rows = [done[it["id"]] for it in items if it["id"] in done]
    common.write_jsonl(out, rows)
    return rows


def evaluate_run(sub: Path, split: str, ragas: bool, run_dir: Path) -> dict:
    cmd = [sys.executable, str(SCRIPTS / "evaluate.py"), "--submission", str(sub), "--split", split,
           "--out", str(run_dir / "reporte.json")]
    if ragas:
        cmd.append("--ragas")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return json.loads((run_dir / "reporte.json").read_text(encoding="utf-8"))


def log_experiment(cfg: Config, rep: dict, run_dir: Path, n_val_errors: int) -> None:
    logs = common.read_jsonl(run_dir / "log.jsonl")
    lat = [l.get("latencia_ms", 0) for l in logs]
    tok = [(l.get("tokens") or {}).get("prompt_tokens", 0) for l in logs]
    rowcsv = {
        "fecha": time.strftime("%Y-%m-%d %H:%M"), "tag": cfg.tag, "config": cfg.hash(),
        "modelo": cfg.model if cfg.backend != "mock" else "mock", "retriever": cfg.retriever,
        "graph": cfg.graph_mode, "k": cfg.k,
        "cerradas": rep["cerradas"]["puntos"], "citas": rep["citas"]["puntos"],
        "abstencion": rep["abstencion"]["puntos"], "ragas": rep["correccion_ragas"].get("puntos"),
        "total": rep["total_automatico"]["obtenidos"], "posibles": rep["total_automatico"]["posibles"],
        "tasa_sin_respaldo": rep["citas"]["tasa_sin_respaldo"],
        "errores_validacion": n_val_errors,
        "abstenciones": sum(1 for l in logs if l.get("abstencion")),
        "fallbacks": sum(len(l.get("fallbacks", [])) for l in logs),
        "latencia_media_ms": int(sum(lat) / max(1, len(lat))),
        "tokens_prompt_medios": int(sum(tok) / max(1, len(tok))),
    }
    p = RUNS / "experimentos.csv"
    new = not p.exists()
    with p.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rowcsv))
        if new:
            w.writeheader()
        w.writerow(rowcsv)
    print(json.dumps(rowcsv, ensure_ascii=False, indent=1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=("sample", "none"), default="sample")
    ap.add_argument("--input", type=Path, default=None)
    ap.add_argument("--config", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--ragas", action="store_true", help="gasta credito de OpenRouter: usar poco")
    ap.add_argument("--fresh", action="store_true", help="ignora la cache de la corrida")
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()

    cfg = Config.load(a.config) if a.config else Config()
    if a.tag:
        cfg.tag = a.tag
    inp = a.input or DATA / "sample_50.jsonl"
    items = load_items(inp)
    run_dir = RUNS / f"{cfg.tag}_{cfg.hash()}"
    if a.fresh and run_dir.exists():
        for f in ("cache.jsonl", "log.jsonl"):
            (run_dir / f).unlink(missing_ok=True)
    out = a.out or run_dir / "submissions.jsonl"
    rows = run(items, cfg, out, run_dir)

    errs = validate_file(rows, {it["id"] for it in items})
    (run_dir / "validacion.txt").write_text("\n".join(errs), encoding="utf-8")
    print(f"[B] {len(rows)} filas -> {out}  | errores de validacion: {len(errs)}", file=sys.stderr)
    for e in errs[:15]:
        print("   ", e, file=sys.stderr)
    if a.split == "sample" and inp.name == "sample_50.jsonl":
        rep = evaluate_run(out, "sample", a.ragas, run_dir)
        log_experiment(cfg, rep, run_dir, len(errs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
