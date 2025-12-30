"""
tests common price parser
"""

from parsers.common_price import CommonPrice
from parsers.row_item.row_item import RowItem

fake_result = [RowItem({"title": 1})]


class FakeParser:
    """fake parser"""

    # pylint: disable=R0903
    _SUPPLIER_FOLDER_NAME = "fake_supplier"

    def __init__(self, file_prices: list | None = None, xls_reader=None, price_config=None) -> None:
        """init"""
        pass

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


def _test_parse_all_vendors() -> None:
    """test parse for each parser in vendor list"""

    common_price = CommonPrice()
    common_price.parse_all_vendors([(FakeParser, None)])
    assert common_price.get_result() == fake_result


def test_suppliers_info() -> None:
    common_price = CommonPrice()
    common_price.supplier_info()
