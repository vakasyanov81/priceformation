# -*- coding: utf-8 -*-
"""
tests for four_tochki vendor (sheet 2) after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List

from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.four_tochki.four_tochki_2sheet import (
    FourTochkiParser2Sheet,
    fourtochki_sheet_2_params,
)
from parsers.xls_reader import FakeXlsReader
from tests.test_parsers.fixtures.four_tochki_sheet2 import four_tochki_one_item_result
from tests.test_parsers.test_vendors.test_mim.price_rules import (
    MimMarkupRulesProviderForTests,
)
from tests.test_parsers.test_vendors.test_parse_poshk import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    StopWordsProviderForTests,
    VendorListProviderForTests,
    vendor_list_config,
)

parser_config = BasePriceParseConfigurationParams(
    black_list_provider=BlackListProviderForTests(),
    markup_rules_provider=MimMarkupRulesProviderForTests(),
    stop_words_provider=StopWordsProviderForTests(),
    vendor_list=VendorListProviderForTests(vendor_list_config),
    manufacturer_aliases=ManufacturerAliasesProviderForTests(),
    parser_params=fourtochki_sheet_2_params,
)


def get_fake_parser(parse_result):
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return FourTochkiParser2Sheet(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


def test_parse():
    """check all field for one price-row"""

    result: List[RowItem] = get_fake_parser(four_tochki_one_item_result()).parse()

    assert len(result) == 1
    assert result[0].title == "6.5x16 5x114.3 ET45 60.1 MBMF Alcasta M35"
    assert result[0].type_production == "Диск"
    assert result[0].price_markup == 8270
    assert result[0].supplier_name == "Форточки"
    assert result[0].percent_markup == 14.7
