# -*- coding: utf-8 -*-
"""
tests for Pioner vendor after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List

import pytest

from src.parsers.base_parser.base_parser_config import (
    ParseConfiguration,
)
from src.parsers.row_item.row_item import RowItem
from src.parsers.vendors.pioner import PionerParser, pioner_params
from src.parsers.xls_reader import FakeXlsReader
from tests.test_parsers.fixtures.pioner import (
    pioner_one_item_result,
    pioner_one_item_result_with_categories,
)
from tests.test_parsers.test_vendors.parse_config import make_parse_configuration

parser_config = make_parse_configuration(pioner_params)


def get_fake_parser(parse_result):
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return PionerParser(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


class TestParsePioner:
    """
    tests for Pioner vendor after raw-parser process
    """

    def test_parse(self):
        """check all field for one price-row"""

        result: List[RowItem] = get_fake_parser(pioner_one_item_result()).parse()

        assert len(result) == 1
        assert result[0].title == "Автокамера 14.00-24"
        assert result[0].price_markup == 2290
        assert result[0].supplier_name == "Пионер"
        assert result[0].percent_markup == 6.82

    def test_parse_brand(self):
        """check all field for one price-row"""

        result: List[RowItem] = get_fake_parser(pioner_one_item_result_with_categories()).parse()

        assert len(result) == 1
        assert result[0].brand == "triangle"

    def test_small_rest(self):
        """test exclude price-position with small rest count"""
        parse_result = pioner_one_item_result()
        first_row = self.get_first_row_item(parse_result)
        first_row.rest_count = 3

        result: List[RowItem] = get_fake_parser(parse_result).parse()

        assert len(result) == 0

    @pytest.mark.parametrize("price_purchase", [0, None])
    def test_null_price_purchase(self, price_purchase):
        """test exclude price-position with null price purchase"""
        parse_result = pioner_one_item_result()
        first_row = self.get_first_row_item(parse_result)
        first_row.price_opt = price_purchase

        result: List[RowItem] = get_fake_parser(parse_result).parse()

        assert len(result) == 0

    def test_small_rest_1(self):
        """test exclude price-position with small rest count"""
        parse_result = pioner_one_item_result()
        first_row = self.get_first_row_item(parse_result)
        first_row.rest_count = 10
        first_row.reserve_count = 7

        result: List[RowItem] = get_fake_parser(parse_result).parse()

        assert len(result) == 0

    @pytest.mark.parametrize(
        "params",
        [{"price": 1000, "price_with_markup": 1040, "category": "автошины xxx"}],
    )
    def test_markup(self, params):
        """test markup"""
        parse_result = pioner_one_item_result_with_categories()
        rows = self.get_rows(parse_result)
        rows[1].title = params.get("category")
        rows[2].price_opt = params.get("price")
        rows[2].price_recommended = params.get("price_recommended")

        result: List[RowItem] = get_fake_parser(parse_result).parse()

        assert len(result) == 1
        assert result[0].price_markup == params.get("price_with_markup")

    @classmethod
    def get_rows(cls, parse_result) -> List[RowItem]:
        """get first item from parse result"""
        file = list(parse_result.keys())[0]
        return [RowItem(item) for item in parse_result[file]]

    @classmethod
    def get_first_row_item(cls, parse_result) -> RowItem:
        """get first item from parse result"""
        return cls.get_rows(parse_result)[0]
