"""Configuracion unica de la capa B. Todo experimento se describe con un Config
y se guarda junto a sus resultados, para poder reproducirlo."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OFICIAL = Path(os.environ.get("HACK_DIR", ROOT / "oficial"))
SCRIPTS = OFICIAL / "scripts"
DATA = OFICIAL / "data"
SCHEMA = OFICIAL / "schema" / "submission.schema.json"
RUNS = ROOT / "runs"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@dataclass
class Config:
    # Decoder (servidor compatible con OpenAI: vLLM, Ollama, llama.cpp server)
    backend: str = "mock"                      # mock | openai
    base_url: str = "http://localhost:8000/v1"
    model: str = "Qwen/Qwen3-8B"
    api_key: str = "EMPTY"
    temperature: float = 0.0
    top_p: float = 1.0
    seed: int = 20261003
    max_tokens: int = 900
    json_mode: str = "schema"                  # schema | object | none
    disable_thinking: bool = True              # Qwen3: enable_thinking=False
    timeout_s: int = 180
    concurrency: int = 8

    # Recuperacion (lo implementa A; B solo consume el contrato)
    retriever: str = "mock"                    # mock | module:funcion
    k: int = 8                                 # pasajes que ve el LLM
    k_submit: int = 10                         # pasajes que se entregan (el evaluador lee 10)
    graph_mode: str = "auto"                   # off | auto | on
    mc_option_queries: bool = True             # consultas extra con cada opcion en cerradas
    max_passage_chars: int = 1800

    # Politica de abstencion
    abstain_min_score: float | None = None     # None = nunca por score
    abstain_if_no_passages: bool = True

    # Citas
    cite_from: str = "used"                    # used | topk | none
    max_cites: int = 6

    tag: str = "dev"
    extra: dict = field(default_factory=dict)

    def hash(self) -> str:
        return hashlib.sha1(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()[:10]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))
