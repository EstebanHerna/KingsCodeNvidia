"""Strict configuration for explicit real-model experiments, separate from 1B."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ..common import ROOT, read_json
from ..model_assets import resolve_model
from ..reasoning.decoder import GENERATION_CONFIG

PROMPT_VERSION = "grounded-formats-v2"


def load_bakeoff(path: Path = ROOT / "config/decoder_bakeoff.json", *, lock_path=ROOT / "config/models.lock.json") -> dict:
    cfg = read_json(path)
    if cfg["generation"] != GENERATION_CONFIG or cfg["prompt_version"] != PROMPT_VERSION:
        raise ValueError("Generation must be greedy/seeded with the versioned prompt")
    if cfg["device"] != "cuda:0" or cfg["precision"]["primary"] != "bf16" or cfg["precision"]["automatic_fallback"] is not False:
        raise ValueError("GPU BF16 first; automatic fallback is forbidden")
    if set(cfg["max_new_tokens"]) != {"multiple_choice", "semi_open", "open_ended"}:
        raise ValueError("Missing format token budgets")
    if any(type(n) is not int or n <= 0 for n in cfg["max_new_tokens"].values()):
        raise ValueError("Invalid output token budget")
    for alias, candidate in cfg["candidates"].items():
        entry = resolve_model(alias, lock_path)
        if candidate["repo_id"] != entry["repo_id"] or candidate["revision"] != entry["revision"]:
            raise ValueError("Candidate does not match its immutable lock")
        if candidate["backend"] != "transformers" or candidate["preferred_dtype"] != "bfloat16":
            raise ValueError("Unsupported backend/dtype")
        if candidate["trust_remote_code"] is not False or candidate["local_files_only"] is not True or candidate["batch_size"] != 1:
            raise ValueError("Only local, trusted-library, batch-one inference is prepared")
        if type(candidate["enabled"]) is not bool or type(candidate["max_context_tokens"]) is not int:
            raise ValueError("Invalid candidate enablement/context")
        if not max(cfg["max_new_tokens"].values()) < candidate["max_context_tokens"] <= 8192:
            raise ValueError("Context must fit the common 8192-token comparison budget")
        expected_template_kwargs = {"enable_thinking": False} if alias == "qwen3-8b" else {}
        if candidate["chat_template_kwargs"] != expected_template_kwargs:
            raise ValueError("Unexpected chat-template overrides")
    if len({c["max_context_tokens"] for c in cfg["candidates"].values()}) != 1:
        raise ValueError("Decoder comparison requires the same context budget")
    return cfg


def select_decoder(alias: str, config: dict, *, allow_optional: bool = False) -> dict:
    if alias not in config["candidates"]:
        raise ValueError(f"Unknown decoder: {alias}")
    candidate = deepcopy(config["candidates"][alias])
    if not candidate["enabled"] and not allow_optional:
        raise ValueError("Optional decoder disabled; select --allow-optional explicitly")
    return candidate
