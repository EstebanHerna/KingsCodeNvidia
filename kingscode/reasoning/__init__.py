"""Member B's CPU-only public interface, independent of retrieval internals."""
from .contracts import Question
from .decoder import DummyDecoder
from .evaluation import run_eval
from .guards import citation_guard, validate_submission
from .pipeline import Pipeline, answer
from .query import normalize_query
from .routing import RetrieverGraphRouter, route_graph

__all__ = ["Question", "DummyDecoder", "Pipeline", "answer", "normalize_query", "route_graph",
           "RetrieverGraphRouter", "citation_guard", "validate_submission", "run_eval"]
