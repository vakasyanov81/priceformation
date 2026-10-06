"""tests for ParseOrchestrator (migrated from test_common_price.py)"""

import logging
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from log_watch import LoggerWatcher, texts_at

from domain.row_item.row_item import RowItem
from parsers.all_vendors import split_vendor_supplier_info
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.parse_statistic import ParserStats
from parsers.registry import UnknownVendorError, make_vendor_entry
from parsers.vendor_config.models import VendorConfig, VendorSection
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
        self.stats = ParserStats()

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
        self.stats = ParserStats(unknown_category_skips=['SUV', 'Foo'])

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
        self.stats = ParserStats(black_list_skips=3)

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


def test_parse_vendor_parse_error_is_logged(watch_logger: LoggerWatcher) -> None:
    """ошибка parse логируется и пробрасывается"""
    parser = MagicMock()
    parser.parse.side_effect = RuntimeError('boom')
    parsed = ParseResult()
    orchestrator = ParseOrchestrator()
    entries = watch_logger(_ORCHESTRATOR_LOGGER, logging.ERROR)

    with pytest.raises(RuntimeError, match='boom'):
        orchestrator._parse_supplier(parsed, parser)

    assert texts_at(entries(), logging.ERROR) == [f'Ошибка разбора прайса поставщика {parser!r} // boom']


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


def test_parse_vendor_without_skips() -> None:
    """парсер без пропусков не добавляет их в результат разбора"""
    parser = MagicMock()
    parser.parse.return_value = []
    parser.stats = ParserStats()
    parsed = ParseResult()
    orchestrator = ParseOrchestrator()

    orchestrator._parse_supplier(parsed, parser)

    assert not parsed.parsed_items
    assert not parsed.unknown_category_skips
    assert parsed.black_list_skips == 0


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


def _disabled_vendor_entry() -> tuple[type[BaseParser], ParseConfiguration]:
    """Создать запись отключённого поставщика."""
    vendor_cfg = VendorConfig(
        folder='test_disabled',
        enabled=False,
        code='99',
        name='TestDisable',
        start_row=1,
    )
    section = VendorSection(
        id='99',
        name='TestDisable',
        start_row=1,
        file_templates=('price*.xls',),
        columns={0: 'title'},
        sheet_indexes=(0,),
    )
    return make_vendor_entry(section, vendor_cfg)


def test_disabled_vendor_is_skipped(watch_logger: LoggerWatcher) -> None:
    vendor_entry = _disabled_vendor_entry()
    orchestrator = ParseOrchestrator()
    entries = watch_logger(_ROW_LOGGER, logging.WARNING)

    parsed = orchestrator.parse_all([vendor_entry])

    assert not parsed.parsed_items
    assert texts_at(entries(), logging.WARNING) == ['поставщик BaseParser: TestDisable не активен']
