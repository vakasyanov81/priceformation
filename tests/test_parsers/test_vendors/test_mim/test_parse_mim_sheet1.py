"""
tests for Mim vendor (sheet 1) after raw-parser process
"""

from typing import List

import pytest
from test_parsers.fixtures.mim_sheet1 import mim_one_item_result
from test_parsers.test_vendors.parse_config import MimMarkupRulesProviderForTests
from test_parsers.test_vendors.parse_result_helpers import get_first_row_item
from test_parsers.test_vendors.test_parse_poshk import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    StopWordsProviderForTests,
    VendorListProviderForTests,
    vendor_list_config,
)

from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.mim.mim_1sheet import (
    MimParser1Sheet,
    mim_sheet_1_params,
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

    row_item = RowItem(
        {
            "title": "",
            "width": row_elements[0],
            "height_percent": row_elements[1],
            "diameter": row_elements[2],
        }
    )
    title = MimParser1Sheet.get_prepared_title(row_item).strip()
    assert title == prepared_title


def test_parse():
    """check all field for one price-row"""

    parsed_items: List[RowItem] = get_fake_parser(mim_one_item_result()).parse()

    assert len(parsed_items) == 1
    assert parsed_items[0].title == "31x10.5R15 Crossleader DSU02 92Y"
    assert parsed_items[0].type_production == "Легковая шина"
    assert parsed_items[0].price_markup == 4220
    assert parsed_items[0].supplier_name == "Мим"
    assert parsed_items[0].percent_markup == 22.07


class TestParseMimSheet1:
    """
    tests for Mim vendor (sheet 1) after raw-parser process
    """

    def test_small_rest(self):
        """test exclude price-position by small rest count"""
        parse_result = mim_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["rest_count"] = 3

        parsed_items: List[RowItem] = get_fake_parser(parse_result).parse()
        assert len(parsed_items) == 0

    @pytest.mark.parametrize(
        "price, price_recommended, price_with_markup",
        [
            (1000, 2000, 2000),
            (1000, 1200, 1500),
            (1000, 1100, 1500),
        ],
    )
    def test_markup(self, price, price_recommended, price_with_markup):
        """test calculation price-markup"""
        parse_result = mim_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["price_opt"] = price
        first_row["price_recommended"] = price_recommended

        parser = get_fake_parser(parse_result)

        parsed_items: List[RowItem] = parser.parse()
        assert parsed_items[0].price_markup == price_with_markup
