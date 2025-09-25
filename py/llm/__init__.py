"""LLM subpackage public API with lazy imports.

Avoid importing heavy dependencies (e.g., optional native extensions) at
package import time. Submodules are loaded on first use.
"""

from __future__ import annotations

__all__ = [
    "generate_prompts",
    "query_llm",
    "bisimulation_similarity",
]


def generate_prompts(*args, **kwargs):  # noqa: D401
    """Proxy for ``py.llm.prompts.generate_prompts``."""
    from .prompts import generate_prompts as _impl
    return _impl(*args, **kwargs)


def query_llm(*args, **kwargs):  # noqa: D401
    """Proxy for ``py.llm.ollama.query_llm``."""
    from .ollama import query_llm as _impl
    return _impl(*args, **kwargs)


def bisimulation_similarity(*args, **kwargs):  # noqa: D401
    """Proxy for ``py.llm.scoring.bisimulation_similarity``."""
    from .scoring import bisimulation_similarity as _impl
    return _impl(*args, **kwargs)
