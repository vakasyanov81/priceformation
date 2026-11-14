"""Интеграционный тест: полный цикл ``uv run pf parse``.

Проверяет, что config-driven парсеры разбирают включённых поставщиков на
эталонных конфигах и прайсах-фикстурах через штатный ParseOrchestrator —
без ошибок и без опоры на боевой ``parse_config/``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from log_watch import LoggerWatcher

from domain.config_context import get_config_provider
from services.parse_orchestrator import ParseOrchestrator
from services.service_provider import ServiceProvider

_INTEGRATION_ROOT = Path(__file__).resolve().parent
_CONFIG_DIR = _INTEGRATION_ROOT / 'parse_config_example'
_ROW_LOGGER = 'parsers.base_parser.row_enricher'


class TestFullParsePipeline:
    """Полный прогон разбора всех включённых поставщиков."""

    def test_migrated_configs_preserve_positions(self, _fixture_config_provider: None) -> None:
        """Все поля позиций совпадают со старой схемой после исправления behavior и назначения ID."""
        baseline = _CONFIG_DIR / 'four_tochki_positions.json'
        expected = json.loads(baseline.read_text(encoding='utf-8'))
        parsed = ServiceProvider.resolve(ParseOrchestrator).parse_all()
        assert [row.to_dict() for row in parsed.tire_and_disk_items] == expected

    def test_all_enabled_vendors_parse_without_errors(
        self,
        _fixture_config_provider: None,
        watch_logger: LoggerWatcher,
    ) -> None:
        """Все включённые поставщики разбираются без ошибок строк.

        Имитирует команду ``uv run pf parse`` — загружает конфиги,
        строит config-driven парсеры, разбирает прайсы.
        """
        watch = watch_logger(_ROW_LOGGER, logging.ERROR)
        parse_output = ServiceProvider.resolve(ParseOrchestrator).parse_all()

        errors = [msg for _level, msg in watch() if 'Не удалось разобрать строку' in msg]
        assert not errors, 'Ошибки разбора: {}'.format('; '.join(errors))
        assert len(parse_output.tire_and_disk_items) > 0
        assert parse_output.tire_and_disk_diagnostics.unknown_category_skips == []

    def test_json_vendor_uses_json_reader(
        self,
        _fixture_config_provider: None,
    ) -> None:
        """Zapaska (reader: json) разбирается через JsonPriceReader, а не XlsReader."""
        from parsers.base_parser.config_driven_parser import make_config_driven_parser
        from parsers.base_parser.file_reader import FileReader
        from parsers.json_reader import JsonPriceReader
        from parsers.registry import vendor_entry_for

        _entry, parse_config = vendor_entry_for('22', get_config_provider())  # zapaska tires
        section = parse_config.vendor_section
        vendor_cfg = parse_config.vendor_config
        from parsers.vendor_config.section_models import VendorSection

        assert isinstance(section, VendorSection)
        assert vendor_cfg is not None

        parser = make_config_driven_parser(section, vendor_cfg, parse_config)
        assert isinstance(parser.price_files.file_reader, FileReader)
        assert (
            parser.price_files.file_reader.data_reader is JsonPriceReader
        ), 'Для json-вендора ожидается JsonPriceReader'

    def test_every_group_has_one_title(self, _fixture_config_provider: None) -> None:
        """В каждой группе по параметрам после разбора ровно одно название."""
        titles_by_group: dict[int | None, set[str | None]] = {}
        for row_item in ServiceProvider.resolve(ParseOrchestrator).parse_all().tire_and_disk_items:
            group_titles = titles_by_group.setdefault(row_item.duplicate.group_by_params, set())
            group_titles.add(row_item.identity.title)

        assert titles_by_group, 'на эталонных прайсах нет ни одной позиции'
        assert all(len(titles) == 1 for titles in titles_by_group.values()), titles_by_group
