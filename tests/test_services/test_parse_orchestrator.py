"""tests for ParseOrchestrator (migrated from test_common_price.py)"""

import logging
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from log_watch import LoggerWatcher, texts_at
from test_parsers.test_vendors import parse_config as vendor_parse_config
from test_parsers.test_vendors import test_parse_poshk

from parsers.all_vendors import split_vendor_supplier_info
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.data_provider import (
    MarkupRulesConfig,
    MarkupRulesProviderBase,
    VendorConfigEntry,
    VendorListProviderBase,
)
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.registry import UnknownVendorError
from parsers.row_item.row_item import RowItem
from parsers.vendors.stk import STKParser, stk_params
from services.parse_orchestrator import ParseOrchestrator, ParseResult

_MOD = 'services.parse_orchestrator'
_ORCHESTRATOR_LOGGER = 'services.parse_orchestrator'
_ROW_LOGGER = 'parsers.base_parser.log_parser_process'


fake_result = [RowItem({'title': 1})]


class FakeParser:
    """fake parser"""

    def __init__(
        self,
        parse_config: Any = None,
        file_prices: list[str] | None = None,
        data_reader: Any = None,
        **kwargs: Any,
    ) -> None:
        """init"""
        self.parse_config = parse_config

    def parse(self) -> list[RowItem]:
        """fake parse"""
        return list(fake_result)


class _SkipSupplier:
    name = 'Запаска (шины)'


class _SkipParserParams:
    supplier = _SkipSupplier()


class FakeParserWithSkips:
    """parser that skipped unknown categories"""

    def __init__(
        self,
        parse_config: Any = None,
        file_prices: list[str] | None = None,
        data_reader: Any = None,
        **kwargs: Any,
    ) -> None:
        """init"""
        self.parse_config = parse_config
        self.unknown_category_skips = ['SUV', 'Foo']

    def parse(self) -> list[RowItem]:
        """fake parse"""
        return []

    def parser_params(self) -> _SkipParserParams:
        """supplier params for skip report"""
        return _SkipParserParams()


class FakeParserWithBlackListSkips:
    """parser that dropped rows by black_list"""

    def __init__(
        self,
        parse_config: Any = None,
        file_prices: list[str] | None = None,
        data_reader: Any = None,
        **kwargs: Any,
    ) -> None:
        """init"""
        self.parse_config = parse_config
        self.black_list_skips = 3

    def parse(self) -> list[RowItem]:
        """fake parse"""
        return []


def test_parse_all() -> None:
    """парсинг списка вендоров и группировка результата"""
    orchestrator = ParseOrchestrator()

    parsed = orchestrator.parse_all([(cast(type[BaseParser], FakeParser), None)])

    assert parsed.parsed_items == fake_result


def test_parse_all_uses_vendors_provider() -> None:
    """parse_all без списка берёт поставщиков из vendors_provider"""
    providers = MagicMock()
    providers.return_value = [(cast(type[BaseParser], FakeParser), None)]
    orchestrator = ParseOrchestrator(vendors_provider=providers)

    parsed = orchestrator.parse_all()

    providers.assert_called_once_with()
    assert parsed.parsed_items == fake_result


def test_parse_vendor_by_code() -> None:
    """parse_vendor разбирает одного поставщика по коду реестра"""
    orchestrator = ParseOrchestrator()
    with patch(f'{_MOD}.vendor_entry_for', return_value=(cast(type[BaseParser], FakeParser), None)):
        parsed = orchestrator.parse_vendor('poshk')

    assert parsed.parsed_items == fake_result


def test_parse_vendor_unknown_code() -> None:
    """неизвестный код поставщика → UnknownVendorError"""
    orchestrator = ParseOrchestrator()
    with (
        patch(f'{_MOD}.vendor_entry_for', side_effect=UnknownVendorError('nope')),
        pytest.raises(UnknownVendorError),
    ):
        orchestrator.parse_vendor('nope')


def test_parse_all_clears_aliases_cache() -> None:
    """каждый прогон сбрасывает кэш aliases и читает карту заново"""
    orchestrator = ParseOrchestrator()
    with (
        patch(f'{_MOD}.clear_manufacturer_aliases_cache') as mock_clear,
        patch('parsers.common_price_grouper.load_aliases_map', return_value={}) as mock_load,
    ):
        orchestrator.parse_all([(cast(type[BaseParser], FakeParser), None)])
        orchestrator.parse_all([(cast(type[BaseParser], FakeParser), None)])
    assert mock_clear.call_count == 2
    assert mock_load.call_count == 2


def test_parse_all_passes_config() -> None:
    """vendor_cls получает переданный vendor_config, не None."""
    vendor_config = MagicMock()
    orchestrator = ParseOrchestrator()
    with patch.object(orchestrator, '_parse_supplier') as mock_parse:
        orchestrator.parse_all([(cast(type[BaseParser], FakeParser), vendor_config)])

    assert mock_parse.call_args is not None
    parser = mock_parse.call_args.args[1]
    assert parser.parse_config is vendor_config


def test_parse_vendor_config_error(watch_logger: LoggerWatcher) -> None:
    """VendorListConfigFileError не валит общий разбор"""
    parser = MagicMock()
    with patch.object(VendorListConfigFileError, 'to_log'):
        parser.parse.side_effect = VendorListConfigFileError('missing')
    parsed = ParseResult()
    orchestrator = ParseOrchestrator()
    entries = watch_logger(_ORCHESTRATOR_LOGGER, logging.WARNING)

    orchestrator._parse_supplier(parsed, parser)

    assert texts_at(entries(), logging.WARNING) == ['Отсутствует файл конфигурации parse_config/vendor_list.json']
    assert not parsed.parsed_items


def test_parse_vendor_reraises(watch_logger: LoggerWatcher) -> None:
    """прочие ошибки логируются и пробрасываются"""
    parser = MagicMock()
    parser.parse.side_effect = RuntimeError('boom')
    parsed = ParseResult()
    orchestrator = ParseOrchestrator()
    entries = watch_logger(_ORCHESTRATOR_LOGGER, logging.ERROR)

    with pytest.raises(RuntimeError, match='boom'):
        orchestrator._parse_supplier(parsed, parser)

    assert texts_at(entries(), logging.ERROR) == [f'Ошибка разбора прайса поставщика {parser!r} // boom']


def test_parse_vendor_skips_bad_counter() -> None:
    """заглушки без int-счётчика не ломают сбор отброшенных по black_list"""
    parser = MagicMock()
    parser.parse.return_value = []
    parser.unknown_category_skips = []
    parsed = ParseResult()
    orchestrator = ParseOrchestrator()

    orchestrator._parse_supplier(parsed, parser)

    assert not parsed.parsed_items


def test_skipped_categories_logged(watch_logger: LoggerWatcher) -> None:
    """пропуски неизвестных категорий печатаются в консоль"""
    orchestrator = ParseOrchestrator()
    entries = watch_logger(_ORCHESTRATOR_LOGGER, logging.WARNING)

    parsed = orchestrator.parse_all([(cast(type[BaseParser], FakeParserWithSkips), None)])

    texts = texts_at(entries(), logging.WARNING)
    assert len(texts) == 1
    message = texts[0]
    assert 'Пропущено 2 позиций' in message
    assert 'Запаска (шины)' in message
    assert 'Foo, SUV' in message
    assert parsed.unknown_category_skips == [
        ('Запаска (шины)', 'SUV'),
        ('Запаска (шины)', 'Foo'),
    ]


_BLACK_LIST_SKIP_LOG = '\nОтброшено 3 позиций по правилам black_list.'


def test_black_list_skips_logged(watch_logger: LoggerWatcher) -> None:
    """отброшенные по black_list позиции печатаются в консоль"""
    orchestrator = ParseOrchestrator()
    entries = watch_logger(_ORCHESTRATOR_LOGGER, logging.INFO)

    parsed = orchestrator.parse_all([(cast(type[BaseParser], FakeParserWithBlackListSkips), None)])

    assert _BLACK_LIST_SKIP_LOG in texts_at(entries(), logging.INFO)
    assert parsed.black_list_skips == 3


def test_suppliers_info() -> None:
    """supplier maps cover vendor codes and do not overlap."""
    enabled, disabled = split_vendor_supplier_info()
    combined = {**enabled, **disabled}
    assert combined['22'] == 'Запаска (шины)'
    assert None not in combined.values()
    assert not set(enabled) & set(disabled)


class _BoomMarkupRules(MarkupRulesProviderBase):
    def get_markup_data(self) -> MarkupRulesConfig:
        raise AssertionError('must not read markup rules')


def test_disabled_vendor_is_skipped(watch_logger: LoggerWatcher) -> None:
    parse_config = ParseConfiguration(
        vendor_parse_config.make_parse_configuration(stk_params, markup_rules=_BoomMarkupRules())._replace(
            vendor_list=test_parse_poshk.VendorListProviderForTests({'stk': {'enabled': 0}}),
        ),
    )
    orchestrator = ParseOrchestrator()
    entries = watch_logger(_ROW_LOGGER, logging.WARNING)

    parsed = orchestrator.parse_all([(STKParser, parse_config)])

    assert not parsed.parsed_items
    assert texts_at(entries(), logging.WARNING) == ['поставщик STKParser: STK не активен']


class _MissingVendorList(VendorListProviderBase):
    def get_config_vendor_list(self) -> dict[str, VendorConfigEntry]:
        raise VendorListConfigFileError('missing')


def test_missing_vendor_list_skips_markup(watch_logger: LoggerWatcher) -> None:
    parse_config = ParseConfiguration(
        vendor_parse_config.make_parse_configuration(stk_params, markup_rules=_BoomMarkupRules())._replace(
            vendor_list=_MissingVendorList(),
        ),
    )
    orchestrator = ParseOrchestrator()
    entries = watch_logger(_ORCHESTRATOR_LOGGER, logging.WARNING)
    with patch.object(VendorListConfigFileError, 'to_log'):
        parsed = orchestrator.parse_all([(STKParser, parse_config)])

    assert not parsed.parsed_items
    warnings = texts_at(entries(), logging.WARNING)
    assert warnings
    assert 'vendor_list.json' in warnings[0]
