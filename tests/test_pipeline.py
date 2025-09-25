import sys
import types
import importlib
import numpy as np

# Stub heavy third-party libs before importing project modules
def _install_stub(name, obj=None):
    if obj is None:
        obj = types.ModuleType(name)
    sys.modules[name] = obj
    return obj

_install_stub('pandas')
_install_stub('matplotlib')
_install_stub('matplotlib.pyplot')
_install_stub('seaborn')
_install_stub('statsmodels')
_install_stub('statsmodels.formula')
_install_stub('statsmodels.formula.api', types.SimpleNamespace(ols=lambda *a, **k: None))
_install_stub('statsmodels.stats')
_install_stub('statsmodels.stats.anova', types.SimpleNamespace(anova_lm=lambda *a, **k: None))


def install_fake_core_rust_for_pipeline():
    S, A = 3, 1
    T = np.zeros((S, A, S), dtype=float)
    for s in range(S):
        T[s, 0, s] = 1.0
    R = np.zeros((S, A), dtype=float)
    R[2, 0] = 1.0
    ideal = [[0, 1], [2]]

    class _PyRunner:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, *args, **kwargs):
            return []

    fake = types.SimpleNamespace(
        get_number_of_states=lambda world: S,
        generate_mdp=lambda world: {"T": T.tolist(), "R": R.tolist(), "abstraction": ideal},
        visualize_abstraction=lambda world, out: None,
        visualize_world_map=lambda world, out: None,
        generate_representations_py=lambda world: {"text": "REP"},
        PyRunner=_PyRunner,
        max_returns=lambda world, gamma: 1.0,
        min_turns=lambda world: 0,
    )
    sys.modules['core_rust'] = fake


def test_evaluate_prompt_with_mocks(monkeypatch):
    install_fake_core_rust_for_pipeline()

    mf = importlib.import_module('llm_abstraction.main_functionality')

    # Replace LLM functions used by evaluate_prompt
    monkeypatch.setattr(mf, 'generate_prompts', lambda compositions, prompts, world: ["PROMPT"])
    monkeypatch.setattr(mf, 'query_llm', lambda prompt, runs, model, num_states, debug=False: {
        "raw_responses": ["raw"],
        "cleaned_responses": [[[0, 1], [2]]],
    })

    general_config = {
        "game": [
            ". . .\n. X .\n. . G"
        ],
        "llm": {
            "tries": 1,
            "compositions": [{
                "instruction": "i1",
                "necessary_context": "nc1",
                "background_contexts": [],
                "representation_key": "text",
                "output": "o1",
            }],
        },
        "mcts_variables": {
            "simulation_limit": [8],
            "simulation_depth": [8],
            "runs": 1,
            "c": 1.4,
            "gamma": 0.9,
            "debug": False,
        }
    }

    prompt_config = {
        "instruction": [{"id": "i1", "val": ""}],
        "necessary_context": [{"id": "nc1", "val": ""}],
        "context": [],
        "output": [{"id": "o1", "val": ""}],
    }

    out = mf.evaluate_prompt(general_config, prompt_config, model="m", prompt_index=0)
    assert isinstance(out, dict) and len(out) == 1
    res = next(iter(out.values()))
    assert res["raw_responses"] == ["raw"]
    assert res["cleaned_responses"] == [[[0, 1], [2]]]
    assert len(res["scores"]) == 1
    # perfect candidate equals ideal ⇒ score should be 1.0
    assert abs(res["scores"][0] - 1.0) < 1e-9
