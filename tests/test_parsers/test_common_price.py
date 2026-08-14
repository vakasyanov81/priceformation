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
    ) -> None:
        """init"""
        self.parse_config = parse_config

    def parse(self) -> list[RowItem]:
        """fake parse"""
        return list(fake_result)


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


def test_common_price_stores_writer_deps() -> None:
    writer_cls = MagicMock()
    driver_cls = MagicMock()
    common_price = CommonPrice(xls_writer=writer_cls, write_driver=driver_cls)
    assert common_price.xls_writer is writer_cls
    assert common_price.write_driver is driver_cls


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


def test_suppliers_info() -> None:
    """supplier_info maps vendor code to supplier name"""
    vendors_by_code = CommonPrice().supplier_info()
    assert vendors_by_code["22"] == "Запаска (шины)"
    assert None not in vendors_by_code.values()
