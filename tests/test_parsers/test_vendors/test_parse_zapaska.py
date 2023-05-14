# -*- coding: utf-8 -*-
"""
tests for zapaska vendor after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List

import pytest

from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.zapaska import zapaska_rest_params
from parsers.vendors.zapaska_rest import ZapaskaRestParser
from parsers.xls_reader import FakeXlsReader
from tests.test_parsers.fixtures.zapaska import zapaska_one_item_result
from tests.test_parsers.test_vendors.test_parse_poshk import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    MarkupRulesProviderForTests,
    StopWordsProviderForTests,
    VendorListProviderForTests,
    vendor_list_config,
)

parser_config = BasePriceParseConfigurationParams(
    black_list_provider=BlackListProviderForTests(),
    markup_rules_provider=MarkupRulesProviderForTests(),
    stop_words_provider=StopWordsProviderForTests(),
    vendor_list=VendorListProviderForTests(vendor_list_config),
    manufacturer_aliases=ManufacturerAliasesProviderForTests(),
    parser_params=zapaska_rest_params,
)


def get_fake_parser(rest_result, parse_result):
    """get fake parser"""
    FakeXlsReader.parse_result = list(rest_result.values())[0]
    return ZapaskaRestParser(
        xls_reader=FakeXlsReader,
        file_prices=list(rest_result.keys()),
        price_mrp=parse_result,
        parse_config=ParseConfiguration(parser_config),
    )


class TestParseZapaska:
    """
    tests for Poshk vendor after raw-parser process
    """

    def test_parse(self):  # pylint: disable=R0201
        """check all field for one price-row"""

        rest_result, parse_result = zapaska_one_item_result()

        result: List[RowItem] = get_fake_parser(rest_result, parse_result).parse()

        res = result[0]

        assert len(result) == 1
        assert res.title == "00 Сельх.шины"
        assert res.price_markup == 4900
        assert res.price_recommended == 4201
        assert res.supplier_name == "Запаска (остатки)"
        assert res.percent_markup == 22.12

    def test_small_rest(self):  # pylint: disable=R0201
        """test exclude price-position with small rest count"""
        rest_result, parse_result = zapaska_one_item_result()
        self.get_first_row_item(rest_result).rest_count = 3

        result: List[RowItem] = get_fake_parser(rest_result, parse_result).parse()

        assert len(result) == 0

    @pytest.mark.parametrize(
        "prices",
        [
            (100, 400, 400),
            (1000, 1100, 1150),
            (10000, 11000, 11000),
            (20000, 20020, 22410),
            (20000, 25000, 25000),
            (60000, 60100, 67200),
        ],
    )
    def test_markup(self, prices):
        """test calculation price-markup"""
        rest_result, parse_result = zapaska_one_item_result()
        price_opt, price_recommended, price_markup = prices
        item = self.get_first_row_item(rest_result)
        item.price_opt = price_opt
        parse_result[0].price_recommended = price_recommended

        result: List[RowItem] = get_fake_parser(rest_result, parse_result).parse()

        assert result[0].price_markup == price_markup

    @classmethod
    def get_first_row_item(cls, parse_result) -> RowItem:
        """get first item from parse result"""
        file = list(parse_result.keys())[0]
        return RowItem(parse_result[file][0])
