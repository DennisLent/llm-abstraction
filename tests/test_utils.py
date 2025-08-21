"""Tests for utility functions in the py.utils package."""

from pathlib import Path
from importlib.machinery import SourceFileLoader

import pytest

module_path = Path(__file__).resolve().parents[1] / "py" / "utils" / "yaml.py"
yaml_utils = SourceFileLoader("yaml_utils", str(module_path)).load_module()
load_config = yaml_utils.load_config
parse_maps = yaml_utils.parse_maps


def test_load_config_reads_yaml(tmp_path: Path) -> None:
    """load_config should parse YAML into a dictionary."""
    config_file = tmp_path / "config.yml"
    config_file.write_text("foo: bar\n")

    cfg = load_config(str(config_file))

    assert cfg == {"foo": "bar"}


def test_parse_maps_returns_grid() -> None:
    """parse_maps should convert YAML map strings into nested lists."""
    yaml_maps = ["A B\nC D"]

    result = parse_maps(yaml_maps)

    assert result == [[["A", "B"], ["C", "D"]]]


def test_parse_maps_raises_on_empty() -> None:
    """parse_maps should error when no maps are provided."""
    with pytest.raises(NameError):
        parse_maps([])
