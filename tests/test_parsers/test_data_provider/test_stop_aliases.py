"""tests for stop words and manufacturer aliases providers"""

from typing import Any
from unittest.mock import patch

import pytest

from parsers.data_provider.manufacturer_aliases import (
    ManufacturerAliasesProviderBase,
    ManufacturerAliasesProviderFromUserConfig,
    drop_blank_aliases,
)
from parsers.data_provider.stop_words import StopWordsProviderBase, StopWordsProviderFromUserConfig


def test_stop_words_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        StopWordsProviderBase().get_stop_words_data()


def test_aliases_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        ManufacturerAliasesProviderBase().get_aliases()


def test_stop_words_from_config() -> None:
    with (
        patch("parsers.data_provider.stop_words.read_file", return_value="w1\nw2"),
        patch("parsers.data_provider.stop_words.MainConfig") as mock_cfg,
    ):
        mock_cfg.return_value.stop_words_file_path = "/sw"
        assert StopWordsProviderFromUserConfig().get_stop_words_data() == ["w1", "w2"]


def test_aliases_from_config() -> None:
    with (
        patch(
            "parsers.data_provider.manufacturer_aliases.read_file",
            return_value='{"A": "B"}',
        ),
        patch("parsers.data_provider.manufacturer_aliases.MainConfig") as mock_cfg,
    ):
        mock_cfg.return_value.manufacturer_aliases_file_path = "/a"
        assert ManufacturerAliasesProviderFromUserConfig().get_aliases() == {"A": "B"}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ({"Brand": [""]}, {"Brand": []}),
        ({"Brand": [" "]}, {"Brand": []}),
        ({"Brand": ["", " ", "Bar"]}, {"Brand": ["Bar"]}),
        ({"Brand": []}, {"Brand": []}),
        ({"A": "B"}, {"A": "B"}),
    ],
)
def test_drop_blank_aliases(raw: Any, expected: Any) -> None:
    assert drop_blank_aliases(raw) == expected


def test_aliases_from_config_drops_blanks() -> None:
    with (
        patch(
            "parsers.data_provider.manufacturer_aliases.read_file",
            return_value='{"Brand": ["", " ", "Bar"]}',
        ),
        patch("parsers.data_provider.manufacturer_aliases.MainConfig") as mock_cfg,
    ):
        mock_cfg.return_value.manufacturer_aliases_file_path = "/a"
        assert ManufacturerAliasesProviderFromUserConfig().get_aliases() == {"Brand": ["Bar"]}
