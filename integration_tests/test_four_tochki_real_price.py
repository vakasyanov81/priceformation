"""Integration test: real four_tochki price parse via entry handlers."""

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from cfg import init_cfg
from infrastructure.config.fake_config_provider import FakeConfigProvider
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
_PRICES_DIR = _INTEGRATION_ROOT / 'file_prices_for_test'
_RESULT_DIR = _INTEGRATION_ROOT / 'result_for_test'
_PARSE_CONFIG_DIR = _INTEGRATION_ROOT / 'parse_config_example'


def _four_tochki_vendors() -> list[tuple[type, object]]:
    """fresh ParseConfiguration per run — instance cache stays empty"""
    return [
        (FourTochkiParser1Sheet, make_parse_config(fourtochki_sheet_1_params)),
        (FourTochkiParser2Sheet, make_parse_config(fourtochki_sheet_2_params)),
    ]


def _clear_result_dir() -> None:
    """очищает каталог результатов перед тестом"""
    _RESULT_DIR.mkdir(parents=True, exist_ok=True)
    for path in _RESULT_DIR.glob('*'):
        if path.is_file():
            path.unlink()


@pytest.fixture
def _example_config() -> Iterator[None]:
    init_cfg(
        FakeConfigProvider(
            _INTEGRATION_ROOT,
            config_folder=_PARSE_CONFIG_DIR,
            prices_folder=_PRICES_DIR,
            result_folder=_RESULT_DIR,
        ),
    )
    yield
    init_cfg()


def test_run_make_price_four_tochki_real(_example_config: None) -> None:
    """разбор реального прайса four_tochki и запись результатов в result_for_test."""
    _clear_result_dir()

    with patch('services.parse_orchestrator.all_vendors', return_value=_four_tochki_vendors()):
        run_make_price_by_supplier()

    result_files = sorted(_RESULT_DIR.glob('*.xlsx'))
    assert result_files, 'ожидались xlsx-файлы в result_for_test'
    assert any('price_' in path.name for path in result_files)
    assert any('drom' in path.name for path in result_files)
    assert all(path.stat().st_size > 0 for path in result_files)
