# -*- coding: utf-8 -*-
"""
tests for Mim vendor (sheet 2) after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List

from parsers.base_parser.base_parser import BasePriceParseConfiguration
from parsers.row_item.row_item import RowItem
from parsers.vendors.mim.mim_2sheet import MimParser2Sheet
from parsers.xls_reader import FakeXlsReader
from tests.test_parsers.fixtures.mim_sheet2 import mim_one_item_result
from tests.test_parsers.test_vendors.test_parse_poshk import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    StopWordsProviderForTests,
    VendorListProviderForTests,
    vendor_list_config,
)

from .price_rules import MimMarkupRulesProviderForTests
from .test_parse_mim_sheet1 import BasePriceParseConfigurationParams

parser_config = BasePriceParseConfigurationParams(
    black_list_provider=BlackListProviderForTests(),
    markup_rules_provider=MimMarkupRulesProviderForTests(),
    stop_words_provider=StopWordsProviderForTests(),
    vendor_list=VendorListProviderForTests(vendor_list_config),
    manufacturer_aliases=ManufacturerAliasesProviderForTests(),
)


def get_fake_parser(parse_result):
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return MimParser2Sheet(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        price_config=BasePriceParseConfiguration(parser_config),
    )


def test_parse():  # pylint: disable=R0201
    """check all field for one price-row"""

    result: List[RowItem] = get_fake_parser(mim_one_item_result()).get_result()

    assert len(result) == 1
    assert result[0].title == "295/75R22.5 Hifly HH312 Ведущая M+S PR16 146/143L TL"
    assert result[0].type_production == "Автошина"
    assert result[0].price_markup == 25990.0
    assert result[0].supplier_name == "Мим"
    assert result[0].percent_markup == 12.03
