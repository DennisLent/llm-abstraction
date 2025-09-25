"""Utilities public API with minimal import-time side effects.

Avoid importing heavy modules (e.g., those that rely on optional native
extensions) at package import time. ``classify_abstraction`` is provided via
lazy proxy to prevent importing ``core_rust`` unless actually used.
"""

from __future__ import annotations

from .yaml import load_config, parse_maps  # re-export lightweight utilities

__all__ = [
    "load_config",
    "parse_maps",
    "classify_abstraction",
]


def classify_abstraction(*args, **kwargs):
    from .classify import classify_abstraction as _impl
    return _impl(*args, **kwargs)
