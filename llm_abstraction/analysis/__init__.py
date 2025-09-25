"""Analysis public API with lazy imports.

Avoid importing heavy dependencies (e.g., statsmodels) during package import.
Each function proxies to its implementation on first use.
"""

from __future__ import annotations

__all__ = [
    "get_info",
    "get_planning_info",
    "perform_ANOVA",
    "perform_ANOVA_z",
    "perform_planning_analysis",
    "plot_distributions",
    "plot_gain_heatmaps",
    "plot_gain_lines",
    "build_full_ranking_table",
    "rank_models",
    "rank_models_prompts",
    "analyze_log_summary",
]


def get_info(*args, **kwargs):
    from .data_collection import get_info as _impl
    return _impl(*args, **kwargs)


def get_planning_info(*args, **kwargs):
    from .data_collection import get_planning_info as _impl
    return _impl(*args, **kwargs)


def perform_ANOVA(*args, **kwargs):
    from .anova import perform_ANOVA as _impl
    return _impl(*args, **kwargs)


def perform_ANOVA_z(*args, **kwargs):
    from .anova import perform_ANOVA_z as _impl
    return _impl(*args, **kwargs)


def perform_planning_analysis(*args, **kwargs):
    from .anova import perform_planning_analysis as _impl
    return _impl(*args, **kwargs)


def plot_distributions(*args, **kwargs):
    from .plots import plot_distributions as _impl
    return _impl(*args, **kwargs)


def plot_gain_heatmaps(*args, **kwargs):
    from .plots import plot_gain_heatmaps as _impl
    return _impl(*args, **kwargs)


def plot_gain_lines(*args, **kwargs):
    from .plots import plot_gain_lines as _impl
    return _impl(*args, **kwargs)


def build_full_ranking_table(*args, **kwargs):
    from .ranking import build_full_ranking_table as _impl
    return _impl(*args, **kwargs)


def rank_models(*args, **kwargs):
    from .ranking import rank_models as _impl
    return _impl(*args, **kwargs)


def rank_models_prompts(*args, **kwargs):
    from .ranking import rank_models_prompts as _impl
    return _impl(*args, **kwargs)


def analyze_log_summary(*args, **kwargs):
    from .log_summary import analyze_log_summary as _impl
    return _impl(*args, **kwargs)
