"""KingsCode knowledge layer. No generation or evaluation labels in the index."""

__all__ = ["Retriever", "retrieve"]


def __getattr__(name):
    if name in __all__:
        from . import retrieval
        return getattr(retrieval, name)
    raise AttributeError(name)
