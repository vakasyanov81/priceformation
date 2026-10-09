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
from services.parse_orchestrator import ParseOrchestrator, ParseResult, _parser_for_vendor

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


@pytest.mark.usefixtures('example_vendors_provider')
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
    assert texts_at(entries(), logging.WARNING) == ['Поставщик TestDisable не активен']


def _config_driven_vendor_entry(
    *,
    enabled: bool = True,
    with_section: bool = True,
    with_config: bool = True,
) -> tuple[VendorSection, VendorConfig, ParseConfiguration]:
    """Запись вендора с возможностью снять ``_vendor_section``/``_vendor_config``."""
    vendor_cfg = VendorConfig(folder='test_folder', enabled=enabled, code='99', name='Test', start_row=1)
    section = VendorSection(
        id='99',
        name='Test',
        start_row=1,
        file_templates=('price*.xls',),
        columns={0: 'title'},
    )
    _, config = make_vendor_entry(section, vendor_cfg)
    if not with_section:
        config._vendor_section = None
    if not with_config:
        config._vendor_config = None
    return section, vendor_cfg, config


def test_parser_for_vendor_without_config() -> None:
    """Без vendor_config класс получает None (легаси-парсер)."""
    vendor_cls = MagicMock()

    _parser_for_vendor(MagicMock(), vendor_cls, None)

    vendor_cls.assert_called_once_with(None)


def test_parser_for_vendor_disabled_uses_parse_config() -> None:
    """Отключённый поставщик строится классом с parse_config."""
    _, _, config = _config_driven_vendor_entry(enabled=False)
    vendor_cls = MagicMock()
    make_cd = MagicMock()

    with patch(f'{_MOD}.make_config_driven_parser', make_cd):
        _parser_for_vendor(MagicMock(), vendor_cls, config)

    vendor_cls.assert_called_once_with(parse_config=config)
    make_cd.assert_not_called()


def test_parser_for_vendor_enabled_with_metadata_builds_config_driven() -> None:
    """Включённый конфиг с секцией и VendorConfig идёт в config-driven фабрику."""
    section, vendor_cfg, config = _config_driven_vendor_entry(enabled=True)
    make_cd = MagicMock(return_value='parser')

    with patch(f'{_MOD}.make_config_driven_parser', make_cd):
        _parser_for_vendor(MagicMock(), MagicMock(), config)

    make_cd.assert_called_once_with(section, vendor_cfg, config)


def test_parser_for_vendor_enabled_without_vendor_config_falls_back() -> None:
    """Без ``_vendor_config`` (не VendorConfig) парсер строится классом."""
    _, _, config = _config_driven_vendor_entry(enabled=True, with_config=False)
    vendor_cls = MagicMock()
    make_cd = MagicMock()

    with patch(f'{_MOD}.make_config_driven_parser', make_cd):
        _parser_for_vendor(MagicMock(), vendor_cls, config)

    vendor_cls.assert_called_once_with(parse_config=config)
    make_cd.assert_not_called()


def test_parser_for_vendor_enabled_without_metadata_falls_back() -> None:
    """Без секции и VendorConfig парсер строится классом."""
    _, _, config = _config_driven_vendor_entry(enabled=True, with_section=False, with_config=False)
    vendor_cls = MagicMock()
    make_cd = MagicMock()

    with patch(f'{_MOD}.make_config_driven_parser', make_cd):
        _parser_for_vendor(MagicMock(), vendor_cls, config)

    vendor_cls.assert_called_once_with(parse_config=config)
    make_cd.assert_not_called()


def test_black_list_skips_accumulate_across_vendors() -> None:
    """Пропуски black_list суммируются по всем поставщикам."""
    orchestrator = ParseOrchestrator()

    parsed = orchestrator.parse_all(
        [
            (cast(type[BaseParser], FakeParserWithBlackListSkips), None),
            (cast(type[BaseParser], FakeParserWithBlackListSkips), None),
        ]
    )

    assert parsed.black_list_skips == 6


def test_parse_vendor_passes_code_to_registry() -> None:
    """parse_vendor передаёт код поставщика в реестр без изменений."""
    orchestrator = ParseOrchestrator()
    entry = (cast(type[BaseParser], FakeParser), None)

    with patch(f'{_MOD}.vendor_entry_for', return_value=entry) as mock_entry:
        orchestrator.parse_vendor('poshk')

    mock_entry.assert_called_once_with('poshk')


def test_parse_vendors_logs_elapsed(watch_logger: LoggerWatcher) -> None:
    """Длительность разбора считается как разность времени старта и конца."""
    orchestrator = ParseOrchestrator()
    entries = watch_logger(_ORCHESTRATOR_LOGGER, logging.INFO)
    ticks = iter([100.0, 101.23])

    with patch(f'{_MOD}.time.monotonic', lambda: next(ticks, 101.23)):
        orchestrator.parse_all([(cast(type[BaseParser], FakeParser), None)])

    assert any('(1.23 сек)' in message for message in texts_at(entries(), logging.INFO))
