"""Validacion de la entrega: esquema JSON oficial + reglas del evaluador."""
from __future__ import annotations

import json

import jsonschema

import evaluate  # modulo oficial

from .config import SCHEMA

_VALIDATOR = jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))


def validate_submission(row: dict) -> list[str]:
    errs = [f"schema: {e.message}" for e in _VALIDATOR.iter_errors(row)]
    errs += [e for e in evaluate.validate([row], {row.get("id")}) if "sin respuesta" not in e]
    if row.get("formato") == "multiple_choice" and not row.get("abstencion"):
        d = row.get("descarte_opciones") or {}
        if row.get("respuesta_correcta") in d:
            errs.append("descarte incluye la opcion elegida")
    if row.get("formato") == "semi_open":
        n = len((row.get("respuesta") or "").split())
        if n > 150:
            errs.append(f"aviso: respuesta de {n} palabras (>150)")
    return errs


def validate_file(rows: list[dict], expected_ids: set[int]) -> list[str]:
    errs = []
    for r in rows:
        errs += [f"{r.get('id')}: {e}" for e in validate_submission(r)]
    errs += [e for e in evaluate.validate(rows, expected_ids) if "sin respuesta" in e]
    return errs
