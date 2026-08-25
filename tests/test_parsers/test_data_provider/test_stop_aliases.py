"""tests for stop words and manufacturer aliases providers"""

from typing import Any
from unittest.mock import patch

import pytest

from core.parse_paths import ParsePaths
from parsers.data_provider.manufacturer_aliases import (
    ManufacturerAliasesProviderBase,
    ManufacturerAliasesProviderFromUserConfig,
    aliases_for_finder,
    drop_blank_aliases,
    load_aliases_map,
)
from parsers.data_provider.manufacturer_group import manufacturer_group
from parsers.data_provider.stop_words import StopWordsProviderBase, StopWordsProviderFromUserConfig

_PATHS = ParsePaths(file_prices_folder="/prices", user_config_folder="/cfg", result_folder="/prices/result")


def test_stop_words_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        StopWordsProviderBase().get_stop_words_data()


def test_aliases_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        ManufacturerAliasesProviderBase().get_aliases()


def test_stop_words_from_config() -> None:
    with (
        patch("parsers.data_provider.stop_words.read_file", return_value="w1\nw2"),
        patch("parsers.data_provider.stop_words.get_parse_paths", return_value=_PATHS),
    ):
        assert StopWordsProviderFromUserConfig().get_stop_words_data() == ["w1", "w2"]


def test_aliases_from_config() -> None:
    with (
        patch(
            "parsers.data_provider.manufacturer_aliases.read_file",
            return_value='{"A": "B"}',
        ),
        patch("parsers.data_provider.manufacturer_aliases.get_parse_paths", return_value=_PATHS),
    ):
        assert ManufacturerAliasesProviderFromUserConfig().get_aliases() == {"A": "B"}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ({"Brand": [""]}, {"Brand": []}),
        ({"Brand": [" "]}, {"Brand": []}),
        ({"Brand": ["", " ", "Bar"]}, {"Brand": ["Bar"]}),
        ({"Brand": []}, {"Brand": []}),
        ({"A": "B"}, {"A": "B"}),
        (
            {"НКШЗ": {"aliases": ["", " ", "НК.ШЗ"], "group": "кама"}},
            {"НКШЗ": {"aliases": ["НК.ШЗ"], "group": "кама"}},
        ),
        (
            {"Aeolus": ["Аеолус"]},
            {"Aeolus": ["Аеолус"]},
        ),
    ],
)
def test_drop_blank_aliases(raw: Any, expected: Any) -> None:
    assert drop_blank_aliases(raw) == expected


def test_aliases_for_finder_object_and_list() -> None:
    raw = {
        "НКШЗ": ["НК.ШЗ", "Нк.шз", "Кама", "Kama"],
        "Aeolus": ["Аеолус"],
        "Cordiant": {"aliases": ["КОРДИАНТ"], "group": "cordiant"},
    }
    assert aliases_for_finder(raw) == {
        "НКШЗ": ("НК.ШЗ", "Нк.шз", "Кама", "Kama"),
        "Aeolus": ("Аеолус",),
        "Cordiant": ("КОРДИАНТ",),
    }


def test_aliases_for_finder_string_and_invalid() -> None:
    assert aliases_for_finder({"A": "B"}) == {"A": ("B",)}
    assert aliases_for_finder({"A": ""}) == {"A": ()}
    assert aliases_for_finder({"A": None}) == {"A": ()}


def test_manufacturer_group_uses_group_or_key() -> None:
    aliases = {
        "НКШЗ": ["НК.ШЗ", "Кама", "Kama"],
        "Aeolus": ["Аеолус"],
        "Cordiant": {"aliases": ["КОРДИАНТ"], "group": "cordiant"},
    }
    assert manufacturer_group("НКШЗ", aliases) == "нкшз"
    assert manufacturer_group("Кама", aliases) == "нкшз"
    assert manufacturer_group("Kama", aliases) == "нкшз"
    assert manufacturer_group("Aeolus", aliases) == "aeolus"
    assert manufacturer_group("Triangle", aliases) == "triangle"
    assert manufacturer_group("", aliases) == ""
    assert manufacturer_group("НКШЗ", {}) == "нкшз"
    assert manufacturer_group("Cordiant", aliases) == "cordiant"
    assert manufacturer_group("Aeolus", {"Aeolus": {"aliases": [], "group": ""}}) == "aeolus"


def test_manufacturer_group_lookup_once_per_map() -> None:
    aliases = {"НКШЗ": ["Кама"]}
    with patch(
        "parsers.data_provider.manufacturer_group.aliases_for_finder",
        wraps=aliases_for_finder,
    ) as finder:
        assert manufacturer_group("Кама", aliases) == "нкшз"
        assert manufacturer_group("НКШЗ", aliases) == "нкшз"
        assert finder.call_count == 1


def test_load_aliases_map_missing_file() -> None:
    load_aliases_map.cache_clear()
    with (
        patch(
            "parsers.data_provider.manufacturer_aliases.read_file",
            side_effect=FileNotFoundError,
        ),
        patch("parsers.data_provider.manufacturer_aliases.get_parse_paths", return_value=_PATHS),
    ):
        assert load_aliases_map() == {}
    load_aliases_map.cache_clear()


def test_aliases_from_config_drops_blanks() -> None:
    with (
        patch(
            "parsers.data_provider.manufacturer_aliases.read_file",
            return_value='{"Brand": ["", " ", "Bar"]}',
        ),
        patch("parsers.data_provider.manufacturer_aliases.get_parse_paths", return_value=_PATHS),
    ):
        assert ManufacturerAliasesProviderFromUserConfig().get_aliases() == {"Brand": ["Bar"]}
