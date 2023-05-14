# -*- coding: utf-8 -*-
"""
tests for Mim vendor (sheet 1) after raw-parser process
"""
__author__ = "Kasyanov V.A."

from typing import List, Tuple

import pytest

from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from parsers.row_item.row_item import RowItem
from parsers.vendors.mim.mim_1sheet import (
    MimParser1Sheet,
    RowItemMim,
    mim_sheet_1_params,
)
from parsers.xls_reader import FakeXlsReader
from tests.test_parsers.fixtures.mim_sheet1 import mim_one_item_result
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
    parser_params=mim_sheet_1_params,
)


def get_fake_parser(parse_result):
    """get fake parser"""
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return MimParser1Sheet(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


@pytest.mark.parametrize(
    "row_elements, prepared_title",
    [
        (("30", "9.5", "15"), "30x9.5R15"),
        (("30", "9.0", "15"), "30x9.0R15"),
        (("30", "9.00", "15"), "30x9.00R15"),
        (("30", "9", "15"), "30/9R15"),
    ],
)
def test_prepare_title(row_elements, prepared_title):
    """check prepare title"""

    item = RowItemMim(
        {
            "title": "",
            "width": row_elements[0],
            "profile": row_elements[1],
            "diameter": row_elements[2],
        }
    )
    title = MimParser1Sheet.get_prepared_title(item).strip()
    assert title == prepared_title


def test_parse():
    """check all field for one price-row"""

    result: List[RowItem] = get_fake_parser(mim_one_item_result()).parse()

    assert len(result) == 1
    assert result[0].title == "31x10.5R15 Crossleader DSU02 92Y"
    assert result[0].type_production == "Автошина"
    assert result[0].price_markup == 4220
    assert result[0].supplier_name == "Мим"
    assert result[0].percent_markup == 22.07


class TestParseMimSheet1:
    """
    tests for Mim vendor (sheet 1) after raw-parser process
    """

    def test_small_rest(self):
        """test exclude price-position by small rest count"""
        parse_result, first_row = self.get_first_row_item(mim_one_item_result())
        first_row.rest_count = 3

        result: List[RowItem] = get_fake_parser(parse_result).parse()
        assert len(result) == 0

    @classmethod
    def get_first_row_item(cls, _result) -> Tuple[dict, RowItem]:
        """get first item from parse result"""
        file = list(_result.keys())[0]
        return _result, RowItem(_result[file][0])

    @pytest.mark.parametrize(
        "price, price_recommended, price_with_markup",
        [
            (1000, 2000, 1270),  # РРЦ выше максимальной наценки
            (1000, 1200, 1200),  # РРЦ ниже максимальной наценки
            (1000, 1100, 1220),  # РРЦ ниже минимальной наценки
        ],
    )
    def test_markup(self, price, price_recommended, price_with_markup):
        """test calculation price-markup"""
        parse_result, first_row = self.get_first_row_item(mim_one_item_result())
        first_row.price_opt = price
        first_row.price_recommended = price_recommended

        parser = get_fake_parser(parse_result)

        result: List[RowItem] = parser.parse()
        assert result[0].price_markup == price_with_markup
