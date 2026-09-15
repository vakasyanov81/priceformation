"""tests for ParseOrchestrator (migrated from test_common_price.py)"""

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from test_parsers import test_vendors

from parsers.all_vendors import split_vendor_supplier_info
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MapOnOptMarkupPolicy,
    MarkupPolicy,
    RecommendedOrMapMarkupPolicy,
    percent_to_store,
)
from parsers.data_provider.markup_rules import MarkupRulesProviderBase
from parsers.data_provider.vendor_list import VendorListConfigFileError, VendorListProviderBase
from parsers.registry import UnknownVendorError
from parsers.row_item.row_item import RowItem
from parsers.vendors.autosnab54_ru import Autosnab54Parser, autosnab_params
from parsers.vendors.four_tochki.four_tochki_sheet1 import (
    FourTochkiParser1Sheet,
    fourtochki_sheet_1_params,
)
from parsers.vendors.pioner import PionerParser, pioner_params
from parsers.vendors.poshk import PoshkParser, poshk_params
from parsers.vendors.stk import STKParser, stk_params
from services.parse_orchestrator import ParseOrchestrator, ParseResult

_MOD = 'services.parse_orchestrator'

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
    with patch(f'{_MOD}.log_msg'):
        parsed = orchestrator.parse_all([(cast(type[BaseParser], FakeParser), None)])
    assert parsed.parsed_items == fake_result


def test_parse_all_uses_vendors_provider() -> None:
    """parse_all без списка берёт поставщиков из vendors_provider"""
    providers = MagicMock()
    providers.return_value = [(cast(type[BaseParser], FakeParser), None)]
    orchestrator = ParseOrchestrator(vendors_provider=providers)
    with patch(f'{_MOD}.log_msg'):
        parsed = orchestrator.parse_all()
    providers.assert_called_once_with()
    assert parsed.parsed_items == fake_result


def test_parse_vendor_by_code() -> None:
    """parse_vendor разбирает одного поставщика по коду реестра"""
    orchestrator = ParseOrchestrator()
    with (
        patch(f'{_MOD}.vendor_entry_for', return_value=(cast(type[BaseParser], FakeParser), None)),
        patch(f'{_MOD}.log_msg'),
    ):
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
        patch(f'{_MOD}.log_msg'),
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
    with (
        patch(f'{_MOD}.log_msg'),
        patch.object(orchestrator, '_parse_supplier') as mock_parse,
    ):
        orchestrator.parse_all([(cast(type[BaseParser], FakeParser), vendor_config)])
    assert mock_parse.call_args is not None
    parser = mock_parse.call_args.args[1]
    assert parser.parse_config is vendor_config


def test_parse_vendor_config_error() -> None:
    """VendorListConfigFileError не валит общий разбор"""
    parser = MagicMock()
    with patch.object(VendorListConfigFileError, 'to_log'):
        parser.parse.side_effect = VendorListConfigFileError('missing')
    parsed = ParseResult()
    orchestrator = ParseOrchestrator()
    with patch(f'{_MOD}.warn_msg') as mock_warn:
        orchestrator._parse_supplier(parsed, parser)
        mock_warn.assert_called_once()
        assert parsed.parsed_items == []


def test_parse_vendor_reraises() -> None:
    """прочие ошибки логируются и пробрасываются"""
    parser = MagicMock()
    parser.parse.side_effect = RuntimeError('boom')
    parsed = ParseResult()
    orchestrator = ParseOrchestrator()
    with patch(f'{_MOD}.err_msg') as mock_err:
        with pytest.raises(RuntimeError, match='boom'):
            orchestrator._parse_supplier(parsed, parser)
        mock_err.assert_called_once()


def test_parse_vendor_skips_bad_counter() -> None:
    """заглушки без int-счётчика не ломают сбор отброшенных по black_list"""
    parser = MagicMock()
    parser.parse.return_value = []
    parser.unknown_category_skips = []
    parsed = ParseResult()
    orchestrator = ParseOrchestrator()
    with patch(f'{_MOD}.log_msg'):
        orchestrator._parse_supplier(parsed, parser)
    assert parsed.parsed_items == []


def test_skipped_categories_logged() -> None:
    """пропуски неизвестных категорий печатаются в консоль"""
    orchestrator = ParseOrchestrator()
    with (
        patch(f'{_MOD}.log_msg'),
        patch(f'{_MOD}.warn_msg') as mock_warn,
    ):
        parsed = orchestrator.parse_all([(cast(type[BaseParser], FakeParserWithSkips), None)])
    mock_warn.assert_called_once()
    message = mock_warn.call_args.args[0]
    assert 'Пропущено 2 позиций' in message
    assert 'Запаска (шины)' in message
    assert 'Foo, SUV' in message
    assert mock_warn.call_args.kwargs['need_print_log'] is True
    assert parsed.unknown_category_skips == [
        ('Запаска (шины)', 'SUV'),
        ('Запаска (шины)', 'Foo'),
    ]


_BLACK_LIST_SKIP_LOG = '\nОтброшено 3 позиций по правилам black_list.'


def test_black_list_skips_logged() -> None:
    """отброшенные по black_list позиции печатаются в консоль"""
    orchestrator = ParseOrchestrator()
    with patch(f'{_MOD}.log_msg') as mock_log:
        parsed = orchestrator.parse_all([(cast(type[BaseParser], FakeParserWithBlackListSkips), None)])
    messages = [call.args[0] for call in mock_log.call_args_list]
    skip_index = messages.index(_BLACK_LIST_SKIP_LOG)
    assert mock_log.call_args_list[skip_index].kwargs['need_print_log'] is True
    assert parsed.black_list_skips == 3


def test_suppliers_info() -> None:
    """supplier maps cover vendor codes and do not overlap."""
    enabled, disabled = split_vendor_supplier_info()
    combined = {**enabled, **disabled}
    assert combined['22'] == 'Запаска (шины)'
    assert None not in combined.values()
    assert not set(enabled) & set(disabled)


def _markup_policy_from_parse_all(parser_cls: type[BaseParser], vendor_params: Any) -> MarkupPolicy:
    config = ParseConfiguration(test_vendors.parse_config.make_parse_configuration(vendor_params))
    orchestrator = ParseOrchestrator()
    with (
        patch(f'{_MOD}.log_msg'),
        patch.object(orchestrator, '_parse_supplier') as mock_parse,
    ):
        orchestrator.parse_all([(parser_cls, config)])
    assert mock_parse.call_args is not None
    parser = mock_parse.call_args.args[1]
    return cast(MarkupPolicy, parser._row_processor._markup_policy)  # noqa: WPS437


@pytest.mark.parametrize(
    ('parser_cls', 'vendor_params'),
    [
        (PoshkParser, poshk_params),
        (PionerParser, pioner_params),
        (STKParser, stk_params),
    ],
)
def test_map_on_opt_vendors_get_map_policy(parser_cls: type[BaseParser], vendor_params: Any) -> None:
    assert isinstance(_markup_policy_from_parse_all(parser_cls, vendor_params), MapOnOptMarkupPolicy)


def test_autosnab_gets_identity_policy() -> None:
    assert isinstance(_markup_policy_from_parse_all(Autosnab54Parser, autosnab_params), IdentityMarkupPolicy)


def test_four_tochki_sheet1_rom_policy() -> None:
    assert isinstance(
        _markup_policy_from_parse_all(FourTochkiParser1Sheet, fourtochki_sheet_1_params),
        RecommendedOrMapMarkupPolicy,
    )


class _BoomMarkupRules(MarkupRulesProviderBase):
    def get_markup_data(self) -> dict[str, Any]:
        raise AssertionError('must not read markup rules')


def test_autosnab_skips_markup_file() -> None:
    config = ParseConfiguration(
        test_vendors.parse_config.make_parse_configuration(autosnab_params, markup_rules=_BoomMarkupRules())
    )
    orchestrator = ParseOrchestrator()
    with (
        patch(f'{_MOD}.log_msg'),
        patch.object(orchestrator, '_parse_supplier') as mock_parse,
    ):
        orchestrator.parse_all([(Autosnab54Parser, config)])
    assert mock_parse.call_args is not None
    parser = mock_parse.call_args.args[1]
    assert isinstance(parser._row_processor._markup_policy, IdentityMarkupPolicy)  # noqa: WPS437


def test_disabled_vendor_is_skipped() -> None:
    parse_config = ParseConfiguration(
        test_vendors.parse_config.make_parse_configuration(stk_params, markup_rules=_BoomMarkupRules())._replace(
            vendor_list=test_vendors.test_parse_poshk.VendorListProviderForTests({'stk': {'enabled': 0}}),
        ),
    )
    orchestrator = ParseOrchestrator()
    with (
        patch(f'{_MOD}.log_msg'),
        patch('parsers.base_parser.log_parser_process.warn_msg') as mock_warn,
    ):
        parsed = orchestrator.parse_all([(STKParser, parse_config)])
    assert parsed.parsed_items == []
    assert mock_warn.call_args is not None
    message = mock_warn.call_args.args[0]
    assert message == 'поставщик STKParser: STK не активен'
    assert mock_warn.call_args.kwargs['need_print_log'] is True


class _MissingVendorList(VendorListProviderBase):
    def get_config_vendor_list(self) -> dict[str, Any]:
        raise VendorListConfigFileError('missing')


def test_missing_vendor_list_skips_markup() -> None:
    parse_config = ParseConfiguration(
        test_vendors.parse_config.make_parse_configuration(stk_params, markup_rules=_BoomMarkupRules())._replace(
            vendor_list=_MissingVendorList(),
        ),
    )
    orchestrator = ParseOrchestrator()
    with (
        patch(f'{_MOD}.log_msg'),
        patch.object(VendorListConfigFileError, 'to_log'),
        patch(f'{_MOD}.warn_msg') as mock_warn,
    ):
        parsed = orchestrator.parse_all([(STKParser, parse_config)])
    assert parsed.parsed_items == []
    assert mock_warn.call_args is not None
    assert 'vendor_list.json' in mock_warn.call_args.args[0]


def test_other_vendor_keeps_default_markup_policy() -> None:
    policy = _markup_policy_from_parse_all(BaseParser, pioner_params)
    assert percent_to_store(policy, 1000) is None
