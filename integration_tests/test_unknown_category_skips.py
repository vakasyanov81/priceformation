"""Интеграционный тест: неизвестные категории поставщика попадают в отчёт о пропусках.

Регресс: ``BaseParser.category_for`` не передавал ``CategoryContext`` в стратегию
``column_canonical``, поэтому флаг ``unknown_skip`` ничего не записывал и
предупреждение о пропущенных категориях (как у Запаски) не выводилось.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
from log_watch import LoggerWatcher, texts_at

from cfg import init_cfg
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.registry import clear_registry
from services.parse_orchestrator import ParseOrchestrator

_ORCHESTRATOR_LOGGER = 'services.parse_orchestrator'
_CASE_ROOT = Path(__file__).resolve().parent / 'unknown_category_case'
_CONFIG_DIR = _CASE_ROOT / 'parse_config'
_PRICES_DIR = _CASE_ROOT / 'file_prices'
_SUPPLIER = 'Тест (шины)'
_UNKNOWN_CATEGORIES = ('SUV', 'Индустриальная')


@pytest.fixture
def _unknown_category_provider(tmp_path: Path) -> Iterator[None]:
    """Изолированные конфиги и прайсы: один JSON-поставщик с `unknown_skip`.

    ``root=tmp_path`` — чтобы логи и результат не появлялись в дереве репозитория.
    """
    init_cfg(
        FakeConfigProvider(
            tmp_path,
            config_folder=_CONFIG_DIR,
            prices_folder=_PRICES_DIR,
            result_folder=tmp_path / 'result',
        ),
    )
    clear_registry()
    yield
    clear_registry()
    init_cfg()


def test_unknown_categories_recorded_and_warned(
    _unknown_category_provider: None,
    watch_logger: LoggerWatcher,
) -> None:
    """Неизвестные категории записываются в результат и печатаются предупреждением."""
    entries = watch_logger(_ORCHESTRATOR_LOGGER, logging.WARNING)

    parsed = ParseOrchestrator().parse_all()

    assert parsed.unknown_category_skips == [(_SUPPLIER, category) for category in _UNKNOWN_CATEGORIES]
    categories_label = ', '.join(_UNKNOWN_CATEGORIES)
    warnings = texts_at(entries(), logging.WARNING)
    assert any('Пропущено 2 позиций' in message for message in warnings)
    assert any(_SUPPLIER in message for message in warnings)
    assert any(f'({categories_label})' in message for message in warnings)
