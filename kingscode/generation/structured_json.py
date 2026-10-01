"""Per-format JSON constraints for the optional XGrammar HF experiment.

The normal strict parser/citation guard remains authoritative. The grammar is a
syntax/type guard during decoding, not a source of legal reasoning.
"""
from __future__ import annotations


def response_schema(fmt: str, options: dict[str, str] | None = None,
                    passage_ids: list[str] | None = None, max_used: int = 5) -> dict:
    ids = list(dict.fromkeys(passage_ids or []))
    properties: dict = {
        "abstencion": {"type": "boolean"},
        "pasajes_usados": {"type": "array", "items": {"type": "string", "enum": ids},
                           "minItems": 1, "maxItems": max_used},
    }
    if fmt == "multiple_choice":
        letters = sorted((options or {}).keys())
        if not letters or any(letter not in {"A", "B", "C", "D"} for letter in letters):
            raise ValueError("multiple_choice grammar requires valid option letters")
        properties.update({
            "respuesta_correcta": {"type": "string", "enum": letters},
            "justificacion": {"type": "string"},
            "descarte_opciones": {"type": "object", "properties": {
                letter: {"type": "string"} for letter in letters}, "additionalProperties": False},
        })
    elif fmt == "semi_open":
        properties.update({"respuesta": {"type": "string"},
                           "palabras_clave": {"type": "array", "items": {"type": "string"}},
                           "referencia_legal": {"type": "string"}})
    elif fmt == "open_ended":
        properties.update({field: {"type": "string"} for field in
                           ("marco_normativo", "analisis", "jurisprudencia", "conclusion")})
    else:
        raise ValueError(f"unsupported response format: {fmt}")
    return {"type": "object", "properties": properties, "required": ["abstencion"],
            "additionalProperties": False}
