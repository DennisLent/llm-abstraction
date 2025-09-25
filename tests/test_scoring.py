import numpy as np
import sys
import types as _types

# Provide a minimal stub for scipy's Wasserstein distance to avoid heavy deps.
_scipy = _types.ModuleType('scipy')
_scipy_stats = _types.ModuleType('scipy.stats')

def _wasserstein_distance(u_values, v_values, u_weights=None, v_weights=None):
    import numpy as _np
    u_values = _np.asarray(u_values)
    v_values = _np.asarray(v_values)
    if u_weights is None:
        u_weights = _np.ones_like(u_values, dtype=float)
    if v_weights is None:
        v_weights = _np.ones_like(v_values, dtype=float)
    mu_u = _np.average(u_values, weights=u_weights)
    mu_v = _np.average(v_values, weights=v_weights)
    return float(abs(mu_u - mu_v))

_scipy_stats.wasserstein_distance = _wasserstein_distance
sys.modules['scipy'] = _scipy
sys.modules['scipy.stats'] = _scipy_stats

from llm_abstraction.llm.scoring import bisimulation_similarity  # noqa: E402


def small_identity_mdp(S=3, A=1):
    T = np.zeros((S, A, S), dtype=float)
    for s in range(S):
        T[s, 0, s] = 1.0
    R = np.zeros((S, A), dtype=float)
    R[2, 0] = 1.0
    return T, R


def test_bisimulation_similarity_identical_is_one():
    T, R = small_identity_mdp()
    ideal = [[0, 1], [2]]
    sim = bisimulation_similarity(ideal, ideal, T, R, c=0.5)
    assert abs(sim - 1.0) < 1e-9


def test_bisimulation_similarity_worse_partition_lower_than_one():
    T, R = small_identity_mdp()
    ideal = [[0, 1], [2]]
    cand = [[0, 1, 2]]
    sim = bisimulation_similarity(cand, ideal, T, R, c=0.5)
    assert 0.0 < sim < 1.0
