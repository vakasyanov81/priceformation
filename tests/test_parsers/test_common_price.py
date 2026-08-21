"""
tests common price parser
"""

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from parsers.base_parser.base_parser import BaseParser
from parsers.common_price import CommonPrice
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.row_item.row_item import RowItem

fake_result = [RowItem({"title": 1})]


class FakeParser:
    """fake parser"""

    def __init__(
        self,
        parse_config: Any = None,
        file_prices: list[str] | None = None,
        xls_reader: Any = None,
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
        xls_reader: Any = None,
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
