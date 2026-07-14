"""tests for stop words and manufacturer aliases providers"""

from unittest.mock import patch

import pytest

from parsers.data_provider.manufacturer_aliases import (
    ManufacturerAliasesProviderBase,
    ManufacturerAliasesProviderFromUserConfig,
)
from parsers.data_provider.stop_words import StopWordsProviderBase, StopWordsProviderFromUserConfig


def test_stop_words_base_raises():
    with pytest.raises(NotImplementedError):
        StopWordsProviderBase().get_stop_words_data()


def test_aliases_base_raises():
    with pytest.raises(NotImplementedError):
        ManufacturerAliasesProviderBase().get_aliases()


def test_stop_words_from_config():
    with (
        patch("parsers.data_provider.stop_words.read_file", return_value="w1\nw2"),
        patch("parsers.data_provider.stop_words.MainConfig") as mock_cfg,
    ):
        mock_cfg.return_value.stop_words_file_path = "/sw"
        assert StopWordsProviderFromUserConfig().get_stop_words_data() == ["w1", "w2"]


def test_aliases_from_config():
    with (
        patch(
            "parsers.data_provider.manufacturer_aliases.read_file",
            return_value='{"A": "B"}',
        ),
        patch("parsers.data_provider.manufacturer_aliases.MainConfig") as mock_cfg,
    ):
        mock_cfg.return_value.manufacturer_aliases_file_path = "/a"
        assert ManufacturerAliasesProviderFromUserConfig().get_aliases() == {"A": "B"}
