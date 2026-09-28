#!/usr/bin/env python3
"""Preflight SIN GPU para KingsCode / Hackathon 2026.

No usa red, no instala paquetes, no carga modelos y no consulta CUDA.
Verifica que el material oficial esté íntegro y que el evaluador determinista
pueda ejecutarse antes de pasar a la etapa GPU.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "data/sample_50.jsonl",
    "data/seed_targets.json",
    "schema/submission.schema.json",
    "scripts/citations.py",
    "scripts/common.py",
    "scripts/evaluate.py",
    "scripts/requirements-evaluador.txt",
    "Ejemplo de entrega/submissions.jsonl",
    "Ejemplo de entrega/corpus_manifest.json",
    "entregables/viernes/REPORTE_AVANCE.md",
    "entregables/sabado/README_EQUIPO.md",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"JSON inválido en {path.relative_to(ROOT)} línea {n}: {exc}") from exc
    return rows


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    missing = [rel for rel in REQUIRED if not (ROOT / rel).is_file()]
    if missing:
        errors.extend(f"Falta archivo obligatorio: {x}" for x in missing)

    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1

    sample = read_jsonl(ROOT / "data/sample_50.jsonl")
    seed = read_json(ROOT / "data/seed_targets.json")
    schema = read_json(ROOT / "schema/submission.schema.json")
    example = read_jsonl(ROOT / "Ejemplo de entrega/submissions.jsonl")
    read_json(ROOT / "Ejemplo de entrega/corpus_manifest.json")

    ids = [r.get("id") for r in sample]
    formats = Counter(r.get("formato") for r in sample)
    areas = Counter(r.get("area") for r in sample)
    if len(sample) != 50:
        errors.append(f"sample_50.jsonl tiene {len(sample)} filas, se esperaban 50")
    if len(set(ids)) != 50:
        errors.append("Los 50 IDs de muestra no son únicos")
    expected_formats = {"multiple_choice": 15, "semi_open": 30, "open_ended": 5}
    if dict(formats) != expected_formats:
        errors.append(f"Distribución de formatos inesperada: {dict(formats)}")
    if len(areas) != 10:
        errors.append(f"La muestra cubre {len(areas)} áreas, se esperaban 10")

    docs = seed.get("documentos") if isinstance(seed, dict) else None
    if not isinstance(docs, list):
        errors.append("seed_targets.json no contiene una lista 'documentos'")
        docs = []
    else:
        if len(docs) != 186:
            warnings.append(f"seed_targets.json contiene {len(docs)} documentos (referencia observada: 186)")
        names = [d.get("norma") for d in docs]
        urls = [d.get("donde_buscar") for d in docs]
        if len(names) != len(set(names)):
            warnings.append("Hay nombres de norma duplicados en seed_targets.json")
        if len(urls) != len(set(urls)):
            warnings.append("Hay URLs duplicadas en seed_targets.json")

    # Verificación sintáctica sin generar __pycache__ ni modificar el árbol oficial.
    for rel in ("scripts/common.py", "scripts/citations.py", "scripts/evaluate.py"):
        try:
            source = (ROOT / rel).read_text(encoding="utf-8")
            compile(source, rel, "exec")
        except SyntaxError as exc:
            errors.append(f"No compila {rel}: {exc}")

    # Ejecuta el evaluador oficial SOLO sobre el ejemplo parcial, sin --ragas.
    # El ejemplo oficial declara que deben faltar 45/50 ítems.
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/evaluate.py"),
             "--submission", str(ROOT / "Ejemplo de entrega/submissions.jsonl"),
             "--split", "sample"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
            env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if proc.returncode != 0:
            errors.append(f"evaluate.py devolvió código {proc.returncode}: {proc.stderr.strip()}")
            eval_report = None
        else:
            eval_report = json.loads(proc.stdout)
            details = eval_report.get("validacion", {}).get("detalle", [])
            if not any("45 items del split sin respuesta" in x for x in details):
                errors.append("El evaluador no produjo el error esperado de 45 ítems faltantes en el ejemplo parcial")
            if eval_report.get("citas", {}).get("aciertos_respaldados") != 7:
                errors.append("El ejemplo oficial no produjo los 7 aciertos de citación respaldados esperados")
    except Exception as exc:
        errors.append(f"No fue posible ejecutar evaluate.py: {exc}")
        eval_report = None

    # Validación JSON Schema opcional; no obliga a instalar nada en esta etapa.
    schema_validation = "omitida (jsonschema no instalado)"
    try:
        from jsonschema import Draft202012Validator  # type: ignore
        validator = Draft202012Validator(schema)
        bad = []
        for row in example:
            errs = list(validator.iter_errors(row))
            if errs:
                bad.append({"id": row.get("id"), "errores": [e.message for e in errs]})
        if bad:
            errors.append(f"El ejemplo oficial no valida contra el schema: {bad}")
        else:
            schema_validation = "OK: 5/5 registros del ejemplo validan"
    except ImportError:
        pass

    report = {
        "ok": not errors,
        "stage": "pre-CUDA",
        "python": sys.version.split()[0],
        "checks": {
            "required_files": f"OK: {len(REQUIRED)}/{len(REQUIRED)}" if not missing else "FALLÓ",
            "sample_rows": len(sample),
            "sample_unique_ids": len(set(ids)),
            "formats": dict(formats),
            "areas": len(areas),
            "seed_documents": len(docs),
            "example_rows": len(example),
            "schema_example": schema_validation,
            "official_example_eval_total_without_ragas": (
                eval_report.get("total_automatico", {}).get("obtenidos") if eval_report else None
            ),
        },
        "warnings": warnings,
        "errors": errors,
    }

    out_dir = ROOT / "artifacts"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "preflight_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
