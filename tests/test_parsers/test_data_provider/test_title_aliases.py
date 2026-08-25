"""tests for title aliases provider"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from core.parse_paths import ParsePaths
from parsers.data_provider.title_aliases import (
    TitleAliasesProviderBase,
    TitleAliasesProviderFromUserConfig,
    invert_title_aliases,
    load_title_aliases,
)
from parsers.vendors import zapaska_disk_json

_PATHS = ParsePaths(file_prices_folder="/prices", user_config_folder="/cfg", result_folder="/prices/result")
_GET_PATHS = "parsers.data_provider.title_aliases.get_parse_paths"
_DISK_SUPPLIER = "Запаска (диски)"
_TIRE_SUPPLIER = "Запаска (шины)"
_ALIASES_JSON = json.dumps(
    {
        _DISK_SUPPLIER: {"Replay Honda": ["Replay HND"]},
        _TIRE_SUPPLIER: {"Three-A": ["THREE-A"]},
    }
)


def test_title_aliases_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        TitleAliasesProviderBase().get_aliases()


def test_invert_title_aliases() -> None:
    assert invert_title_aliases({"Good": ["Bad", "Worse"]}) == {"Bad": "Good", "Worse": "Good"}


def test_load_title_aliases_missing_file() -> None:
    with (
        patch("parsers.data_provider.title_aliases.read_file", side_effect=FileNotFoundError),
        patch(_GET_PATHS, return_value=_PATHS),
    ):
        assert load_title_aliases(_DISK_SUPPLIER) == {}


def test_load_aliases_inverts_supplier_section() -> None:
    with (
        patch("parsers.data_provider.title_aliases.read_file", return_value=_ALIASES_JSON) as mock_read,
        patch(_GET_PATHS, return_value=_PATHS),
    ):
        assert load_title_aliases(_DISK_SUPPLIER) == {"Replay HND": "Replay Honda"}
        assert load_title_aliases(_TIRE_SUPPLIER) == {"THREE-A": "Three-A"}
        assert load_title_aliases("unknown") == {}
        mock_read.assert_called_with("/cfg/title_aliases.json")


def test_load_title_aliases_from_real_file(tmp_path: Path) -> None:
    (tmp_path / "title_aliases.json").write_text(_ALIASES_JSON, encoding="utf-8")
    paths = ParsePaths(
        file_prices_folder=str(tmp_path),
        user_config_folder=str(tmp_path),
        result_folder=str(tmp_path),
    )
    with patch(_GET_PATHS, return_value=paths):
        assert load_title_aliases(_DISK_SUPPLIER) == {"Replay HND": "Replay Honda"}


def test_provider_reads_parse_paths_config_file() -> None:
    with (
        patch("parsers.data_provider.title_aliases.read_file", return_value="{}") as mock_read,
        patch(_GET_PATHS, return_value=_PATHS),
    ):
        assert TitleAliasesProviderFromUserConfig(_DISK_SUPPLIER).get_aliases() == {}
        mock_read.assert_called_once_with("/cfg/title_aliases.json")


def test_zapaska_disk_json_does_not_import_cfg() -> None:
    source = Path(zapaska_disk_json.__file__).read_text(encoding="utf-8")
    assert "from cfg" not in source
    assert "import cfg" not in source
