import types
import sys
import importlib
import pytest


def install_fake_core_rust(repr_map: dict):
    fake = types.SimpleNamespace(generate_representations_py=lambda world: repr_map)
    sys.modules['core_rust'] = fake


def test_generate_prompts_success(monkeypatch):
    repr_map = {"text": "GRID-TEXT", "json": {"grid": [[".", "."], [".", "G"]]}}
    install_fake_core_rust(repr_map)

    prompts_mod = importlib.import_module('py.llm.prompts')

    compositions = [{
        "instruction": "i1",
        "necessary_context": "nc1",
        "background_contexts": ["c1", "c2"],
        "representation_key": "text",
        "output": "o1"
    }]

    prompt_defs = {
        "instruction": [{"id": "i1", "val": "Do the thing."}],
        "necessary_context": [{"id": "nc1", "val": "You must follow the rules."}],
        "context": [
            {"id": "c1", "val": "Background A."},
            {"id": "c2", "val": "Background B."},
        ],
        "output": [{"id": "o1", "val": "Return JSON only."}],
    }

    world = [[".", "."], [".", "G"]]
    out = prompts_mod.generate_prompts(compositions, prompt_defs, world)
    assert len(out) == 1
    text = out[0]
    assert "Do the thing." in text
    assert "You must follow the rules." in text
    assert "Background A." in text and "Background B." in text
    assert "GRID-TEXT" in text
    assert "Return JSON only." in text


def test_generate_prompts_missing_ids_raise(monkeypatch):
    repr_map = {"text": "REP"}
    install_fake_core_rust(repr_map)
    prompts_mod = importlib.reload(importlib.import_module('py.llm.prompts'))

    compositions = [{
        "instruction": "missing",
        "necessary_context": "nc1",
        "background_contexts": [],
        "representation_key": "text",
        "output": "o1"
    }]

    prompt_defs = {
        "instruction": [{"id": "i1", "val": "Do the thing."}],
        "necessary_context": [{"id": "nc1", "val": "Rules."}],
        "context": [],
        "output": [{"id": "o1", "val": "Return JSON only."}],
    }

    with pytest.raises(KeyError):
        prompts_mod.generate_prompts(compositions, prompt_defs, world=[["."]])

