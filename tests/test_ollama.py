import types
import importlib
import sys


def stub_chat_sequence(outputs):
    """Return a stub whose chat() yields successive dict outputs or raises."""
    it = iter(outputs)

    class Stub:
        def chat(self, model, messages, stream=False):
            val = next(it)
            if isinstance(val, Exception):
                raise val
            return {"message": {"content": val}}

    return Stub()


def test_run_ollama_collects_non_empty(monkeypatch):
    # Ensure module 'ollama' exists before importing impl
    sys.modules['ollama'] = types.SimpleNamespace()
    mod = importlib.import_module('llm_abstraction.llm.ollama')
    # Simulate: error, empty, 'a', 'b' for runs=2
    stub = stub_chat_sequence([RuntimeError("boom"), "", "first", "second"])
    monkeypatch.setattr(mod, 'ollama', stub)
    out = mod._run_ollama(prompt="p", runs=2, model="m", debug=True)
    assert out == ["first", "second"]


def test_reprompt_llm_strips_code_fences(monkeypatch):
    sys.modules['ollama'] = types.SimpleNamespace()
    mod = importlib.import_module('llm_abstraction.llm.ollama')
    fenced = "```json\n[[0,1],[2]]\n```"
    stub = stub_chat_sequence([fenced])
    monkeypatch.setattr(mod, 'ollama', stub)
    out = mod._reprompt_llm(["anything"], model="m")
    assert out == ['[[0,1],[2]]']


def test_query_llm_orchestrates(monkeypatch):
    sys.modules['ollama'] = types.SimpleNamespace()
    mod = importlib.import_module('llm_abstraction.llm.ollama')
    # Patch internals to avoid real model calls
    monkeypatch.setattr(mod, '_run_ollama', lambda prompt, need, model, debug=False: ["raw"])
    monkeypatch.setattr(mod, '_clean_responses', lambda raw_responses, model, num_states: [[[0], [1]]])
    result = mod.query_llm(prompt="p", runs=1, model="m", num_states=2, debug=False)
    assert result == {"raw_responses": ["raw"], "cleaned_responses": [[[0], [1]]]} 
