"""Parity test: config-driven parser works end-to-end on integration fixtures.

Проверяет, что config-driven парсер (через эталонные
``integration_tests/parse_config_example/vendors/*.json``) корректно разбирает
фикстурный прайс four_tochki через штатный ParseOrchestrator.
"""

import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
from log_watch import LoggerWatcher

from cfg import init_cfg
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.registry import clear_registry, vendor_entry_for
from services.parse_orchestrator import ParseOrchestrator

_INTEGRATION_ROOT = Path(__file__).resolve().parent
_PRICES_DIR = _INTEGRATION_ROOT / 'file_prices_for_test'
_CONFIG_DIR = _INTEGRATION_ROOT / 'parse_config_example'
_ROW_LOGGER = 'parsers.base_parser.base_parser_row'


@pytest.fixture
def _four_tochki_provider() -> Iterator[None]:
    """Провайдер путей: и конфиги, и цены — из фикстур (без боевого parse_config)."""
    init_cfg(
        FakeConfigProvider(
            _INTEGRATION_ROOT,
            config_folder=_CONFIG_DIR,
            prices_folder=_PRICES_DIR,
            result_folder=_INTEGRATION_ROOT / 'result_for_test',
        ),
    )
    clear_registry()
    yield
    clear_registry()
    init_cfg()


class TestFourTochkiConfigDriven:
    """Config-driven разбор four_tochki через ParseOrchestrator."""

    def test_config_driven_parse_has_no_errors(
        self,
        _four_tochki_provider: None,
        watch_logger: LoggerWatcher,
    ) -> None:
        """Разбор real прайса без ошибок строк."""
        watch = watch_logger(_ROW_LOGGER, logging.ERROR)
        errors = [msg for _level, msg in watch() if 'Не удалось разобрать строку' in msg]
        assert not errors, f'Есть ошибки разбора строк:\n{errors}'

        parsed = ParseOrchestrator().parse_all([vendor_entry_for('5')])
        assert parsed.parsed_items, 'Нет разобранных строк'
        assert parsed.unknown_category_skips == []

    def test_all_vendors_catalog_has_eight_entries(
        self,
        _four_tochki_provider: None,
    ) -> None:
        """Каталог содержит 8 записей — проверка что реестр читает все конфиги."""
        from parsers.all_vendors import all_vendor_supplier_info

        supplier_info = all_vendor_supplier_info()
        assert len(supplier_info) == 8, f'Ожидалось 8 записей, получено {len(supplier_info)}'
        # Коды: 1-пошк, 2-запаска(диски), 22-запаска(шины), 3-пионер,
        # 4-мим, 5-форточки, 6-автоснабжение, 7-STK
        assert set(supplier_info) == {'1', '2', '22', '3', '4', '5', '6', '7'}

    def test_parse_all_warns_about_disabled_vendors(
        self,
        _four_tochki_provider: None,
        watch_logger: LoggerWatcher,
    ) -> None:
        """parse_all логирует предупреждение о каждом отключённом поставщике.

        В фикстурах включён только four_tochki, остальные (pioner, stk, mim,
        poshk, zapaska, autosnab) — отключены и должны попасть в лог как «не активен».
        """
        entries = watch_logger('parsers.base_parser.log_parser_process', logging.WARNING)

        ParseOrchestrator().parse_all()

        warnings = [message for _level, message in entries() if 'не активен' in message]
        assert warnings, 'Нет предупреждений об отключённых поставщиках'
        assert any('Пионер' in message for message in warnings)
        assert any('STK' in message for message in warnings)
        assert all(
            'Форточки' not in message for message in warnings
        ), 'four_tochki включён, предупреждения быть не должно'


class TestSupplierCatalog:
    """Проверка that внешние ИД каталога не изменились."""

    def test_get_suppliers_returns_eight_entries(
        self,
        _four_tochki_provider: None,
    ) -> None:
        """8 записей поставщиков."""
        from parsers.all_vendors import all_vendor_supplier_catalog

        catalog = all_vendor_supplier_catalog()
        assert len(catalog) == 8, f'Ожидалось 8 записей, получено {len(catalog)}'
        assert set(catalog) == {'1', '2', '22', '3', '4', '5', '6', '7'}

    def test_zapaska_has_two_ids(
        self,
        _four_tochki_provider: None,
    ) -> None:
        """Запаска: два ИД — 2 (диски) и 22 (шины)."""
        from parsers.all_vendors import all_vendor_supplier_info

        supplier_info = all_vendor_supplier_info()
        assert supplier_info.get('2') == 'Запаска (диски)'
        assert supplier_info.get('22') == 'Запаска (шины)'
