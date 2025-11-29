# -*- coding: utf-8 -*-
"""
tests for Mim vendor (sheet 2) after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List

from parsers.base_parser.base_parser import ParseConfiguration
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.mim.mim_2sheet import MimParser2Sheet, mim_sheet_2_params
from test_parsers.fixtures.mim_sheet2 import mim_one_item_result
from test_parsers.test_vendors.test_parse_poshk import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    StopWordsProviderForTests,
    VendorListProviderForTests,
    vendor_list_config,
)
from .test_parse_mim_sheet1 import BasePriceParseConfigurationParams
from ..parse_config import MimMarkupRulesProviderForTests

parser_config = BasePriceParseConfigurationParams(
    black_list_provider=BlackListProviderForTests(),
    markup_rules_provider=MimMarkupRulesProviderForTests(),
    stop_words_provider=StopWordsProviderForTests(),
    vendor_list=VendorListProviderForTests(vendor_list_config),
    manufacturer_aliases=ManufacturerAliasesProviderForTests(),
    parser_params=mim_sheet_2_params,
)


def get_fake_parser(parse_result):
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return MimParser2Sheet(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


def test_parse():
    """check all field for one price-row"""

    result: List[RowItem] = get_fake_parser(mim_one_item_result()).parse()

    assert len(result) == 1
    assert result[0].title == "295/75R22.5 Hifly HH312 PR16 146/143L TL Ведущая M+S"
    assert result[0].type_production == "Грузовая шина"
    assert result[0].price_markup == 24360.0
    assert result[0].supplier_name == "Мим"
    assert result[0].percent_markup == 5
