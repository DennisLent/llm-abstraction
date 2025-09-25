"""Top-level package exports for the prototype.

This module intentionally avoids importing heavy submodules at import time
to keep ``import py`` safe during testing (e.g., when optional native
extensions like ``core_rust`` are not built). Public functions are exposed
via lightweight proxies that import on first use.
"""

from __future__ import annotations

# ``load_config`` is lightweight; re-export directly.
from .utils import load_config  # noqa: F401

__all__ = [
    "preview_prompts",
    "mcts",
    "evaluate_prompt",
    "preview_maps",
    "llm_abstraction",
    "analysis",
    "load_config",
]

# Lazy, on-demand imports to avoid importing ``core_rust`` at module import time.

def preview_prompts(*args, **kwargs):  # noqa: D401
    """Proxy for ``py.main_functionality.preview_prompts``."""
    from .main_functionality import preview_prompts as _impl
    return _impl(*args, **kwargs)


def mcts(*args, **kwargs):  # noqa: D401
    """Proxy for ``py.main_functionality.mcts``."""
    from .main_functionality import mcts as _impl
    return _impl(*args, **kwargs)


def evaluate_prompt(*args, **kwargs):  # noqa: D401
    """Proxy for ``py.main_functionality.evaluate_prompt``."""
    from .main_functionality import evaluate_prompt as _impl
    return _impl(*args, **kwargs)


def preview_maps(*args, **kwargs):  # noqa: D401
    """Proxy for ``py.main_functionality.preview_maps``."""
    from .main_functionality import preview_maps as _impl
    return _impl(*args, **kwargs)


def llm_abstraction(*args, **kwargs):  # noqa: D401
    """Proxy for ``py.main_functionality.llm_abstraction``."""
    from .main_functionality import llm_abstraction as _impl
    return _impl(*args, **kwargs)


def analysis(*args, **kwargs):  # noqa: D401
    """Proxy for ``py.main_functionality.analysis``."""
    from .main_functionality import analysis as _impl
    return _impl(*args, **kwargs)
