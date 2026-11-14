"""Parity test: config-driven parser works end-to-end on integration fixtures.

Проверяет, что config-driven парсер (через эталонные
``integration_tests/parse_config_example/vendors/*.json``) корректно разбирает
фикстурный прайс four_tochki через штатный ParseOrchestrator.
"""

import logging

from log_watch import LoggerWatcher

from domain.config_context import get_config_provider
from parsers.registry import vendor_entry_for
from services.parse_orchestrator import ParseOrchestrator
from services.service_provider import ServiceProvider

_ROW_LOGGER = 'parsers.base_parser.row_enricher'
_MIM_IDS = ('4', '42', '43')
_FOUR_TOCHKI_IDS = ('5', '55')
_OTHER_IDS = ('1', '2', '22', '3', '6', '7')
_SECTION_IDS = frozenset((*_OTHER_IDS, *_MIM_IDS, *_FOUR_TOCHKI_IDS, 'plant_batteries'))


class TestFourTochkiConfigDriven:
    """Config-driven разбор four_tochki через ParseOrchestrator."""

    def test_config_driven_parse_has_no_errors(
        self,
        _fixture_config_provider: None,
        watch_logger: LoggerWatcher,
    ) -> None:
        """Разбор real прайса без ошибок строк."""
        watch = watch_logger(_ROW_LOGGER, logging.ERROR)
        parsed = ServiceProvider.resolve(ParseOrchestrator).parse_all([vendor_entry_for('5', get_config_provider())])

        errors = [msg for _level, msg in watch() if 'Не удалось разобрать строку' in msg]
        assert not errors, f'Есть ошибки разбора строк:\n{errors}'

        assert parsed.tire_and_disk_items, 'Нет разобранных строк'
        assert parsed.tire_and_disk_diagnostics.unknown_category_skips == []

    def test_catalog_contains_every_section(
        self,
        _fixture_config_provider: None,
    ) -> None:
        """Каталог содержит отдельную запись каждой из 12 секций."""
        from parsers.all_vendors import all_vendor_supplier_info

        supplier_info = all_vendor_supplier_info(get_config_provider())
        # Коды: 1-пошк, 2-запаска(диски), 22-запаска(шины), 3-пионер,
        # 4/42/43-мим, 5/55-форточки, 6-автоснабжение, 7-STK
        assert set(supplier_info) == _SECTION_IDS

    def test_parse_all_warns_about_disabled_vendors(
        self,
        _fixture_config_provider: None,
        watch_logger: LoggerWatcher,
    ) -> None:
        """parse_all логирует предупреждение о каждом отключённом поставщике.

        В фикстурах включён только four_tochki, остальные (pioner, stk, mim,
        poshk, zapaska, autosnab) — отключены и должны попасть в лог как «не активен».
        """
        entries = watch_logger('parsers.base_parser.log_parser_process', logging.WARNING)

        ServiceProvider.resolve(ParseOrchestrator).parse_all()

        warnings = [message for _level, message in entries() if 'не активен' in message]
        assert warnings, 'Нет предупреждений об отключённых поставщиках'
        assert any('Пионер' in message for message in warnings)
        assert any('STK' in message for message in warnings)
        assert all(
            'Форточки' not in message for message in warnings
        ), 'four_tochki включён, предупреждения быть не должно'


class TestSupplierCatalog:
    """Проверка внешних ИД каталога после устранения коллизий секций."""

    def test_suppliers_have_unique_sections(
        self,
        _fixture_config_provider: None,
    ) -> None:
        """Все 12 секций доступны по согласованным уникальным ключам."""
        from parsers.all_vendors import all_vendor_supplier_catalog

        catalog = all_vendor_supplier_catalog(get_config_provider())
        assert set(catalog) == _SECTION_IDS
        assert catalog['55']['sup_code'] == 'four_tochki'
        assert catalog['42']['sup_code'] == catalog['43']['sup_code'] == 'mim'

    def test_zapaska_has_two_ids(
        self,
        _fixture_config_provider: None,
    ) -> None:
        """Запаска: два ИД — 2 (диски) и 22 (шины)."""
        from parsers.all_vendors import all_vendor_supplier_info

        supplier_info = all_vendor_supplier_info(get_config_provider())
        assert supplier_info.get('2') == 'Запаска (диски)'
        assert supplier_info.get('22') == 'Запаска (шины)'
