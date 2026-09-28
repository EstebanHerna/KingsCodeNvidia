"""Public inputs only: labels never cross the generation boundary."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json

FORMATS = ("multiple_choice", "semi_open", "open_ended")
ANSWER_FIELDS = {
    "multiple_choice": ("respuesta_correcta", "justificacion", "descarte_opciones"),
    "semi_open": ("respuesta", "palabras_clave", "referencia_legal"),
    "open_ended": ("marco_normativo", "analisis", "jurisprudencia", "conclusion"),
}


@dataclass(frozen=True)
class Question:
    id: int
    text: str
    format: str
    options: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if type(self.id) is not int or not isinstance(self.text, str) or self.format not in FORMATS:
            raise ValueError("Question requires integer id, text and an official format")
        if not isinstance(self.options, dict) or any(k not in "ABCD" or len(k) != 1 or not isinstance(v, str)
                                                    for k, v in self.options.items()):
            raise ValueError("Options must contain only A/B/C/D and plain text")

    def public_record(self) -> dict:
        return {"id": self.id, "pregunta": self.text, "formato": self.format, "opciones": dict(self.options)}


def public_question(record: dict) -> Question:
    """Allowlist projection, including nested options; never pass the raw row on."""
    return Question(record["id"], record["pregunta"], record["formato"], dict(record.get("opciones") or {}))


def load_questions(path: Path) -> list[Question]:
    questions = []
    with path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            if line.strip():
                questions.append(public_question(json.loads(line)))
    if len({q.id for q in questions}) != len(questions):
        raise ValueError("Duplicate question IDs")
    return questions
