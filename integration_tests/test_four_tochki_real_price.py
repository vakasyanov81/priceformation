"""Integration test: real four_tochki price parse via entry handlers."""

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from cfg import init_cfg
from cfg.main import MainConfig
from core.parse_paths import ParsePaths, configure_parse_paths
from parsers.base_parser import nomenclature_correction as noc
from parsers.base_parser.base_parser_config import make_parse_config
from parsers.vendors.four_tochki.four_tochki_sheet1 import (
    FourTochkiParser1Sheet,
    fourtochki_sheet_1_params,
)
from parsers.vendors.four_tochki.four_tochki_sheet2 import (
    FourTochkiParser2Sheet,
    fourtochki_sheet_2_params,
)
from run import run_make_price_by_supplier

_INTEGRATION_ROOT = Path(__file__).resolve().parent
_PRICES_REL = "integration_tests/file_prices_for_test"
_RESULT_DIR = _INTEGRATION_ROOT / "result_for_test"
_PARSE_CONFIG_DIR = _INTEGRATION_ROOT / "parse_config_example"
_PARSE_CONFIG = f"{_PARSE_CONFIG_DIR.as_posix()}/"
_RESULT_PATH = f"{_RESULT_DIR.as_posix()}/"


def _four_tochki_vendors() -> list[tuple[type, object]]:
    """fresh ParseConfiguration per run — instance cache stays empty"""
    return [
        (FourTochkiParser1Sheet, make_parse_config(fourtochki_sheet_1_params)),
        (FourTochkiParser2Sheet, make_parse_config(fourtochki_sheet_2_params)),
    ]


def _result_folder(_cfg: MainConfig) -> str:
    """тестовая папка результатов"""
    return _RESULT_PATH


def _reset_nomenclature_cache() -> None:
    """сбрасывает кэш номенклатуры между прогонами"""
    noc._NomenclatureCache.titles = None  # noqa: WPS437


def _clear_result_dir() -> None:
    """очищает каталог результатов перед тестом"""
    _RESULT_DIR.mkdir(parents=True, exist_ok=True)
    for path in _RESULT_DIR.glob("*"):
        if path.is_file():
            path.unlink()


@pytest.fixture
def _example_parse_paths() -> Iterator[None]:
    configure_parse_paths(
        ParsePaths(
            file_prices_folder=str(Path(MainConfig().project_root) / _PRICES_REL),
            user_config_folder=_PARSE_CONFIG,
        ),
    )
    yield
    init_cfg()


def test_run_make_price_four_tochki_real(_example_parse_paths: None) -> None:
    """разбор реального прайса four_tochki и запись результатов в result_for_test."""
    _clear_result_dir()
    _reset_nomenclature_cache()

    with (
        patch.object(MainConfig, "result_folder_path", property(_result_folder)),
        patch("run.all_vendors", return_value=_four_tochki_vendors()),
    ):
        run_make_price_by_supplier()

    result_files = sorted(_RESULT_DIR.glob("*.xlsx"))
    assert result_files, "ожидались xlsx-файлы в result_for_test"
    assert any("price_" in path.name for path in result_files)
    assert any("drom" in path.name for path in result_files)
    assert all(path.stat().st_size > 0 for path in result_files)
