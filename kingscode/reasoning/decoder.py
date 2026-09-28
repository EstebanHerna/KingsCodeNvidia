"""Offline backend contract. Dummy is deliberately incapable of legal answers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import Question
from .guards import evidence_record

PROMPT_VERSION = "grounded-formats-v1"
GENERATION_CONFIG = {"temperature": 0.0, "do_sample": False, "seed": 0}


@dataclass(frozen=True)
class PromptSpec:
    format: str
    version: str = PROMPT_VERSION
    instruction: str = "Use only supplied evidence. Abstain when it is insufficient. Return the official JSON format."


class Decoder(Protocol):
    name: str
    version: str

    def generate(self, question: Question, passages: list[dict], prompt: PromptSpec, generation: dict) -> dict: ...


def abstention_row(question: Question, passages: list[dict], reason: str) -> dict:
    row = {"id": question.id, "formato": question.format, "abstencion": True,
           "pasajes_recuperados": [evidence_record(p) for p in passages[:10]]}
    if question.format == "multiple_choice":
        # Official schema's prose permits null, but its actual enum does not.
        # Preserve schema bytes and never present the required placeholder as a choice.
        row.update(respuesta_correcta="A", justificacion=(
            f"Abstención automática ({reason}). A es un marcador formal exigido por el schema; no representa una elección de respuesta."),
            descarte_opciones={})
    elif question.format == "semi_open":
        row.update(respuesta="", palabras_clave=[], referencia_legal="")
    else:
        row.update(marco_normativo="", analisis="", jurisprudencia="", conclusion="")
    return row


class DummyDecoder:
    name = "dummy_abstain"
    version = "1"

    def generate(self, question, passages, prompt, generation):
        if generation != GENERATION_CONFIG or prompt.format != question.format:
            raise ValueError("Deterministic generation/prompt contract violated")
        return abstention_row(question, passages, "dummy_backend_no_legal_reasoning")
