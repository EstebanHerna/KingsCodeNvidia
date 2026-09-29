"""Read-only access to the official citation extractor (scripts/citations.py).

Loaded by path under a private module name so B scores support with the exact
code the jury runs, without editing or copying the official file.
"""
from __future__ import annotations

from functools import lru_cache
import importlib.util

from ..common import ROOT


@lru_cache(maxsize=1)
def citations():
    spec = importlib.util.spec_from_file_location("kingscode_official_citations", ROOT / "scripts/citations.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def official_bodies(text: str) -> set[tuple]:
    mod = citations()
    return mod.bodies(mod.extract(text or ""))


def evidence_bodies(passages: list[dict]) -> set[tuple]:
    """Bodies the official evaluator counts as supported: first 10 passages' text."""
    found: set[tuple] = set()
    for p in passages[:10]:
        found |= official_bodies(p.get("texto") or p.get("text") or "")
    return found
