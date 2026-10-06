"""Интеграционный тест: полный цикл ``uv run pf parse``.

Проверяет, что config-driven парсеры разбирают ВСЕХ включённых поставщиков
с реальными прайсами через штатный ParseOrchestrator — без ошибок.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
from log_watch import LoggerWatcher

from cfg import init_cfg
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.registry import clear_registry
from services.parse_orchestrator import ParseOrchestrator

_INTEGRATION_ROOT = Path(__file__).resolve().parent
_PROJECT_ROOT = _INTEGRATION_ROOT.parent
_ROW_LOGGER = 'parsers.base_parser.base_parser_row'


@pytest.fixture
def _real_config_provider() -> Iterator[None]:
    """Провайдер путей: и конфиги, и цены — из настоящего репозитория."""
    init_cfg(
        FakeConfigProvider(
            _PROJECT_ROOT,
            config_folder=_PROJECT_ROOT / 'parse_config',
            prices_folder=_PROJECT_ROOT / 'file_prices',
            result_folder=_PROJECT_ROOT / 'file_prices' / 'result',
        ),
    )
    clear_registry()
    yield
    clear_registry()
    init_cfg()


class TestFullParsePipeline:
    """Полный прогон разбора всех включённых поставщиков."""

    def test_all_enabled_vendors_parse_without_errors(
        self,
        _real_config_provider: None,
        watch_logger: LoggerWatcher,
    ) -> None:
        """Все включённые поставщики разбираются без ошибок строк.

        Имитирует команду ``uv run pf parse`` — загружает конфиги,
        строит config-driven парсеры, разбирает прайсы.
        """
        watch = watch_logger(_ROW_LOGGER, logging.ERROR)
        parse_output = ParseOrchestrator().parse_all()

        errors = [msg for _level, msg in watch() if 'Не удалось разобрать строку' in msg]
        assert not errors, 'Ошибки разбора: {}'.format('; '.join(errors))
        assert len(parse_output.parsed_items) > 0
        assert parse_output.unknown_category_skips == []

    def test_json_vendor_uses_json_reader(
        self,
        _real_config_provider: None,
    ) -> None:
        """Zapaska (reader: json) разбирается через JsonPriceReader, а не XlsReader."""
        from parsers.base_parser.config_driven_parser import make_config_driven_parser
        from parsers.json_reader import JsonPriceReader
        from parsers.registry import vendor_entry_for

        _entry, parse_config = vendor_entry_for('22')  # zapaska tires
        section = parse_config._vendor_section
        vendor_cfg = parse_config._vendor_config

        parser = make_config_driven_parser(section, vendor_cfg, parse_config)
        assert (
            parser.data_reader is JsonPriceReader
        ), f'Для json-вендора ожидается JsonPriceReader, получен {parser.data_reader}'

        # Файлы есть — разбор не должен упасть с CalamineError
        assert parser._file_reader_impl._data_reader is JsonPriceReader  # type: ignore[attr-defined]
