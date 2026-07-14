"""Integration test: real four_tochki price parse via entry handlers."""

from pathlib import Path
from unittest.mock import patch

from cfg.main import MainConfig
from parsers.base_parser.nomenclature_correction import get_nomenclature_corrected_title
from parsers.vendors.four_tochki.four_tochki_sheet1 import (
    FourTochkiParser1Sheet,
    fourtochki_sheet_1_config,
)
from parsers.vendors.four_tochki.four_tochki_sheet2 import (
    FourTochkiParser2Sheet,
    fourtochki_sheet_2_config,
)
from run import run_make_price_by_supplier

_INTEGRATION_ROOT = Path(__file__).resolve().parent
_PROJECT_ROOT = _INTEGRATION_ROOT.parent
_PRICES_REL = "integration_tests/file_prices_for_test"
_RESULT_DIR = _INTEGRATION_ROOT / "result_for_test"
_PARSE_CONFIG_DIR = _PROJECT_ROOT / "parse_config_example"
_PARSE_CONFIG = f"{_PARSE_CONFIG_DIR.as_posix()}/"
_RESULT_PATH = f"{_RESULT_DIR.as_posix()}/"

_FOUR_TOCHKI_VENDORS = (
    (FourTochkiParser1Sheet, fourtochki_sheet_1_config),
    (FourTochkiParser2Sheet, fourtochki_sheet_2_config),
)


def _prices_folder(_cfg: MainConfig) -> str:
    """тестовая папка с прайсами"""
    return _PRICES_REL


def _result_folder(_cfg: MainConfig) -> str:
    """тестовая папка результатов"""
    return _RESULT_PATH


def _user_config_folder(_cfg: MainConfig) -> str:
    """конфиг из parse_config_example для CI"""
    return _PARSE_CONFIG


def _reset_four_tochki_config_cache() -> None:
    """сбрасывает кэш конфигов four_tochki между прогонами"""
    for config in (fourtochki_sheet_1_config, fourtochki_sheet_2_config):
        config._all_vendor_config = None  # noqa: WPS437
        config._markup_rules = None  # noqa: WPS437
        config._price_markup_map = None  # noqa: WPS437
    get_nomenclature_corrected_title.corrected_nomenclatures_ = None


def _clear_result_dir() -> None:
    """очищает каталог результатов перед тестом"""
    _RESULT_DIR.mkdir(parents=True, exist_ok=True)
    for path in _RESULT_DIR.glob("*"):
        if path.is_file():
            path.unlink()


def test_run_make_price_four_tochki_real():
    """разбор реального прайса four_tochki и запись результатов в result_for_test."""
    _clear_result_dir()
    _reset_four_tochki_config_cache()

    with (
        patch.object(MainConfig, "folder_file_prices", property(_prices_folder)),
        patch.object(MainConfig, "result_folder_path", property(_result_folder)),
        patch.object(MainConfig, "user_config_folder_path", property(_user_config_folder)),
        patch("run.all_vendors", return_value=_FOUR_TOCHKI_VENDORS),
    ):
        run_make_price_by_supplier()

    result_files = sorted(_RESULT_DIR.glob("*.xlsx"))
    assert result_files, "ожидались xlsx-файлы в result_for_test"
    assert any("price_" in path.name for path in result_files)
    assert any("drom" in path.name for path in result_files)
    assert all(path.stat().st_size > 0 for path in result_files)
