"""
tests common price parser
"""

from unittest.mock import MagicMock, patch

import pytest

from parsers.common_price import CommonPrice
from parsers.data_provider.vendor_list import VendorListConfigFileError
from parsers.row_item.row_item import RowItem

fake_result = [RowItem({"title": 1})]


class FakeParser:
    """fake parser"""

    # pylint: disable=R0903
    _SUPPLIER_FOLDER_NAME = "fake_supplier"  # noqa: WPS115

    def __init__(self, file_prices: list | None = None, xls_reader=None, price_config=None):
        """init"""

    @classmethod
    def supplier_folder_name(cls):
        """supplier folder name"""
        return cls._SUPPLIER_FOLDER_NAME

    @classmethod
    def get_result(cls):
        """fake get result"""
        return fake_result

    @classmethod
    def parse(cls):
        """fake get result"""
        return fake_result


def test_parse_all_vendors():
    """парсинг списка вендоров и группировка результата"""
    common_price = CommonPrice()
    with patch("parsers.common_price.log_msg"):
        common_price.parse_all_vendors([(FakeParser, None)])
    assert common_price.result == fake_result


def test_parse_vendor_config_error():
    """VendorListConfigFileError не валит общий разбор"""
    parser = MagicMock()
    with patch.object(VendorListConfigFileError, "to_log"):
        parser.parse.side_effect = VendorListConfigFileError("missing")
    common_price = CommonPrice()

    with patch("parsers.common_price.warn_msg") as mock_warn:
        common_price.parse_vendor(parser)
        mock_warn.assert_called_once()
        assert common_price.result == []


def test_parse_vendor_reraises():
    """прочие ошибки логируются и пробрасываются"""
    parser = MagicMock()
    parser.parse.side_effect = RuntimeError("boom")
    common_price = CommonPrice()

    with patch("parsers.common_price.err_msg") as mock_err:
        with pytest.raises(RuntimeError, match="boom"):
            common_price.parse_vendor(parser)
        mock_err.assert_called_once()


def test_suppliers_info():
    """supplier_info returns dict"""
    common_price = CommonPrice()
    assert isinstance(common_price.supplier_info(), dict)
