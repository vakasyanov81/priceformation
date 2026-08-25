"""
tests common price parser
"""

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest
from test_parsers.test_vendors.parse_config import make_parse_configuration
from test_parsers.test_vendors.test_parse_poshk import VendorListProviderForTests

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MapOnOptMarkupPolicy,
    MarkupPolicy,
    RecommendedOrMapMarkupPolicy,
    percent_to_store,
)
from parsers.common_price import CommonPrice
from parsers.data_provider.markup_rules import MarkupRulesProviderBase
from parsers.data_provider.vendor_list import VendorListConfigFileError, VendorListProviderBase
from parsers.row_item.row_item import RowItem
from parsers.vendors.autosnab54_ru import Autosnab54Parser, autosnab_params
from parsers.vendors.four_tochki.four_tochki_sheet1 import (
    FourTochkiParser1Sheet,
    fourtochki_sheet_1_params,
)
from parsers.vendors.pioner import PionerParser, pioner_params
from parsers.vendors.poshk import PoshkParser, poshk_params
from parsers.vendors.stk import STKParser, stk_params

fake_result = [RowItem({"title": 1})]


class FakeParser:
    """fake parser"""

    def __init__(
        self,
        parse_config: Any = None,
        file_prices: list[str] | None = None,
        data_reader: Any = None,
        *,
        markup_policy: Any = None,
    ) -> None:
        """init"""
        self.parse_config = parse_config

    def parse(self) -> list[RowItem]:
        """fake parse"""
        return list(fake_result)


class _SkipSupplier:
    name = "Запаска (шины)"


class _SkipParserParams:
    supplier = _SkipSupplier()


class FakeParserWithSkips:
    """parser that skipped unknown categories"""

    def __init__(
        self,
        parse_config: Any = None,
        file_prices: list[str] | None = None,
        data_reader: Any = None,
        *,
        markup_policy: Any = None,
    ) -> None:
        """init"""
        self.parse_config = parse_config
        self.unknown_category_skips = ["SUV", "Foo"]

    def parse(self) -> list[RowItem]:
        """fake parse"""
        return []

    def parser_params(self) -> _SkipParserParams:
        """supplier params for skip report"""
        return _SkipParserParams()


def test_parse_all_vendors() -> None:
    """парсинг списка вендоров и группировка результата"""
    common_price = CommonPrice()
    with patch("parsers.common_price.log_msg"):
        common_price.parse_all_vendors([(cast(type[BaseParser], FakeParser), None)])
    assert common_price.parsed_items == fake_result


def test_parse_all_vendors_passes_config() -> None:
    """vendor_cls получает переданный vendor_config, не None."""
    vendor_config = MagicMock()
    common_price = CommonPrice()
    with (
        patch("parsers.common_price.log_msg"),
        patch.object(common_price, "parse_vendor") as mock_parse,
    ):
        common_price.parse_all_vendors(
            [(cast(type[BaseParser], FakeParser), vendor_config)],
        )
    assert mock_parse.call_args is not None
    parser = mock_parse.call_args.args[0]
    assert parser.parse_config is vendor_config


def test_parse_vendor_config_error() -> None:
    """VendorListConfigFileError не валит общий разбор"""
    parser = MagicMock()
    with patch.object(VendorListConfigFileError, "to_log"):
        parser.parse.side_effect = VendorListConfigFileError("missing")
    common_price = CommonPrice()

    with patch("parsers.common_price.warn_msg") as mock_warn:
        common_price.parse_vendor(parser)
        mock_warn.assert_called_once()
        assert common_price.parsed_items == []


def test_parse_vendor_reraises() -> None:
    """прочие ошибки логируются и пробрасываются"""
    parser = MagicMock()
    parser.parse.side_effect = RuntimeError("boom")
    common_price = CommonPrice()

    with patch("parsers.common_price.err_msg") as mock_err:
        with pytest.raises(RuntimeError, match="boom"):
            common_price.parse_vendor(parser)
        mock_err.assert_called_once()


def test_skipped_categories_logged() -> None:
    """пропуски неизвестных категорий печатаются в консоль"""
    common_price = CommonPrice()
    with (
        patch("parsers.common_price.log_msg"),
        patch("parsers.common_price.warn_msg") as mock_warn,
    ):
        common_price.parse_all_vendors([(cast(type[BaseParser], FakeParserWithSkips), None)])
    mock_warn.assert_called_once()
    message = mock_warn.call_args.args[0]
    assert "Пропущено 2 позиций" in message
    assert "Запаска (шины)" in message
    assert "Foo, SUV" in message
    assert mock_warn.call_args.kwargs["need_print_log"] is True


def test_suppliers_info() -> None:
    """supplier_info maps vendor code to supplier name"""
    vendors_by_code = CommonPrice().supplier_info()
    assert vendors_by_code["22"] == "Запаска (шины)"
    assert None not in vendors_by_code.values()


def _markup_policy_from_parse_all(parser_cls: type[BaseParser], vendor_params: Any) -> MarkupPolicy:
    config = ParseConfiguration(make_parse_configuration(vendor_params))
    common_price = CommonPrice()
    with (
        patch("parsers.common_price.log_msg"),
        patch.object(common_price, "parse_vendor") as mock_parse,
    ):
        common_price.parse_all_vendors([(parser_cls, config)])
    assert mock_parse.call_args is not None
    parser = mock_parse.call_args.args[0]
    return cast(MarkupPolicy, parser._markup_policy)  # noqa: WPS437


@pytest.mark.parametrize(
    ("parser_cls", "vendor_params"),
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
        raise AssertionError("must not read markup rules")


def test_autosnab_skips_markup_file() -> None:
    config = ParseConfiguration(make_parse_configuration(autosnab_params, markup_rules=_BoomMarkupRules()))
    common_price = CommonPrice()
    with (
        patch("parsers.common_price.log_msg"),
        patch.object(common_price, "parse_vendor") as mock_parse,
    ):
        common_price.parse_all_vendors([(Autosnab54Parser, config)])
    assert mock_parse.call_args is not None
    parser = mock_parse.call_args.args[0]
    assert isinstance(parser._markup_policy, IdentityMarkupPolicy)  # noqa: WPS437


def test_disabled_vendor_is_skipped() -> None:
    parse_config = ParseConfiguration(
        make_parse_configuration(stk_params, markup_rules=_BoomMarkupRules())._replace(
            vendor_list=VendorListProviderForTests({"stk": {"enabled": 0}}),
        ),
    )
    common_price = CommonPrice()
    with (
        patch("parsers.common_price.log_msg"),
        patch("parsers.base_parser.log_parser_process.warn_msg") as mock_warn,
    ):
        common_price.parse_all_vendors([(STKParser, parse_config)])
    assert common_price.parsed_items == []
    assert mock_warn.call_args is not None
    message = mock_warn.call_args.args[0]
    assert message == "поставщик STKParser: STK не активен"
    assert mock_warn.call_args.kwargs["need_print_log"] is True


class _MissingVendorList(VendorListProviderBase):
    def get_config_vendor_list(self) -> dict[str, Any]:
        raise VendorListConfigFileError("missing")


def test_missing_vendor_list_skips_markup() -> None:
    parse_config = ParseConfiguration(
        make_parse_configuration(stk_params, markup_rules=_BoomMarkupRules())._replace(
            vendor_list=_MissingVendorList(),
        ),
    )
    common_price = CommonPrice()
    with (
        patch("parsers.common_price.log_msg"),
        patch.object(VendorListConfigFileError, "to_log"),
        patch("parsers.common_price.warn_msg") as mock_warn,
    ):
        common_price.parse_all_vendors([(STKParser, parse_config)])
    assert common_price.parsed_items == []
    assert mock_warn.call_args is not None
    assert "vendor_list.json" in mock_warn.call_args.args[0]


def test_other_vendor_keeps_default_markup_policy() -> None:
    policy = _markup_policy_from_parse_all(BaseParser, pioner_params)
    assert percent_to_store(policy, 1000) is None
