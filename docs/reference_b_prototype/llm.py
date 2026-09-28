"""Backends del decoder. 'openai' sirve para vLLM, Ollama (/v1) y llama.cpp
server, todos con API compatible con OpenAI. 'mock' permite probar todo sin GPU."""
from __future__ import annotations

import json
import time

import requests

from .config import Config


class LLMError(RuntimeError):
    pass


def chat(cfg: Config, messages: list[dict], schema: dict | None = None) -> tuple[str, dict]:
    if cfg.backend == "mock":
        return _mock(messages, schema), {"prompt_tokens": 0, "completion_tokens": 0}
    if cfg.extra.get("no_think_tag"):   # Ollama + Qwen3: desactiva el modo thinking
        messages = messages[:-1] + [{**messages[-1], "content": messages[-1]["content"] + " /no_think"}]
    body = {"model": cfg.model, "messages": messages, "temperature": cfg.temperature,
            "top_p": cfg.top_p, "seed": cfg.seed, "max_tokens": cfg.max_tokens}
    if cfg.json_mode == "schema" and schema:
        body["response_format"] = {"type": "json_schema",
                                   "json_schema": {"name": "respuesta", "schema": schema}}
    elif cfg.json_mode in ("schema", "object"):
        body["response_format"] = {"type": "json_object"}
    if cfg.disable_thinking:
        body["chat_template_kwargs"] = {"enable_thinking": False}   # vLLM + Qwen3
    body.update(cfg.extra.get("request", {}))
    last = None
    for attempt in range(3):
        try:
            r = requests.post(cfg.base_url.rstrip("/") + "/chat/completions", json=body,
                              headers={"Authorization": f"Bearer {cfg.api_key}"}, timeout=cfg.timeout_s)
            if r.status_code == 400 and "response_format" in body and attempt == 0:
                body["response_format"] = {"type": "json_object"}   # servidor sin json_schema
                continue
            r.raise_for_status()
            d = r.json()
            return d["choices"][0]["message"]["content"] or "", d.get("usage", {})
        except Exception as e:  # red, timeout, 5xx
            last = e
            time.sleep(2 * (attempt + 1))
    raise LLMError(str(last))


def _mock(messages: list[dict], schema: dict | None) -> str:
    props = (schema or {}).get("properties", {})
    if "analisis_opciones" in props:
        return json.dumps({"pasajes_usados": [1], "analisis_opciones": {k: "mock" for k in "ABCD"},
                           "respuesta": "A", "justificacion": "Respuesta simulada con base en [P1]."})
    if "palabras_clave" in props:
        return json.dumps({"pasajes_usados": [1], "respuesta": "Respuesta simulada con base en la evidencia [P1].",
                           "palabras_clave": ["mock"]})
    return json.dumps({"pasajes_usados": [1], "marco_normativo": "Marco simulado.", "analisis": "Análisis simulado.",
                       "jurisprudencia": "No se identificó jurisprudencia específica en la evidencia recuperada.",
                       "conclusion": "Conclusión simulada."})
