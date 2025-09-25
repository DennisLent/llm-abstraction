import pytest

from py.llm.clean import _extract_grouping, clean_with_regex_and_validate


def test_extract_grouping_json_simple():
    resp = "[[0,1],[2]]"
    out = _extract_grouping(resp, num_states=3)
    assert out == [[0, 1], [2]]


def test_extract_grouping_handles_strings_and_invalids():
    # includes an out-of-range value 3 that should be dropped
    resp = "[[ \"0\", \"3\" ], [1, 1, 2]]"
    out = _extract_grouping(resp, num_states=3)
    assert out == [[0], [1, 2]]


def test_extract_grouping_with_labels_and_brackets():
    resp = """
    Cluster 1: [0, 2]
    Cluster 2: [1]
    """
    out = _extract_grouping(resp, num_states=3)
    assert out == [[0, 2], [1]]


def test_extract_grouping_from_code_fence():
    resp = """```json\n[[0,1],[2]]\n```"""
    out = _extract_grouping(resp, num_states=3)
    assert out == [[0, 1], [2]]


def test_missing_states_are_appended():
    resp = "[[0]]"
    out = _extract_grouping(resp, num_states=3)
    # states 1 and 2 should be appended as a final group
    assert out == [[0], [1, 2]]


def test_clean_with_regex_and_validate_batches():
    responses = ["[[0,1]]", "nonsense", "[0]\n[1]"]
    cleaned = clean_with_regex_and_validate(responses, num_states=2)
    assert cleaned[0] == [[0, 1]]
    assert cleaned[1] is None
    assert cleaned[2] == [[0], [1]]

