"""
tests for Pioner vendor after raw-parser process
"""

from typing import List

import pytest
from test_parsers.fixtures.pioner import (
    pioner_one_item_result,
    pioner_one_item_result_with_categories,
)
from test_parsers.test_vendors.parse_config import (
    PionerMarkupRulesProviderForTests,
    make_parse_configuration,
)
from test_parsers.test_vendors.parse_result_helpers import get_first_row_item, get_rows

from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
)
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.pioner import PionerParser, pioner_params

parser_config = make_parse_configuration(pioner_params, markup_rules=PionerMarkupRulesProviderForTests())


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

        parsed_items: List[RowItem] = get_fake_parser(pioner_one_item_result()).parse()

        assert len(parsed_items) == 1
        assert parsed_items[0].title == "Автокамера 14.00-24"
        assert parsed_items[0].price_markup == 2310
        assert parsed_items[0].supplier_name == "Пионер"
        assert parsed_items[0].percent_markup == 5

    def test_parse_brand(self):
        """check all field for one price-row"""

        parsed_items: List[RowItem] = get_fake_parser(pioner_one_item_result_with_categories()).parse()

        assert len(parsed_items) == 1
        assert parsed_items[0].brand == "triangle"

    def test_small_rest(self):
        """test exclude price-position with small rest count"""
        parse_result = pioner_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["rest_count"] = 3

        parsed_items: List[RowItem] = get_fake_parser(parse_result).parse()

        assert len(parsed_items) == 0

    @pytest.mark.parametrize("price_opt", [0, None])
    def test_null_price_opt(self, price_opt):
        """test exclude price-position with null price purchase"""
        parse_result = pioner_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["price_opt"] = price_opt

        parsed_items: List[RowItem] = get_fake_parser(parse_result).parse()

        assert len(parsed_items) == 0

    def test_small_rest_1(self):
        """test exclude price-position with small rest count"""
        parse_result = pioner_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["rest_count"] = 10
        first_row["reserve_count"] = 7

        parsed_items: List[RowItem] = get_fake_parser(parse_result).parse()

        assert len(parsed_items) == 0

    @pytest.mark.parametrize(
        "markup_case",
        [
            # {"price": 1000, "price_with_markup": 1200, "category": "автошины xxx"},
            # {"price": 1500, "price_with_markup": 1770, "category": "автошины xxx"},
            # {"price": 6000, "price_with_markup": 6730, "category": "автошины xxx"},
            # {"price": 20000, "price_with_markup": 21400, "category": "автошины xxx"},
            {
                "price": 150000,
                "price_with_markup": 157500,
                "category": "автошины TRIANGLE",
            },
        ],
    )
    def test_markup(self, markup_case):
        """test markup"""
        parse_result = pioner_one_item_result_with_categories()
        rows = get_rows(parse_result)
        rows[1]["title"] = markup_case.get("category")
        rows[2]["price_opt"] = markup_case.get("price")
        rows[2]["price_recommended"] = markup_case.get("price_recommended")

        parsed_items: List[RowItem] = get_fake_parser(parse_result).parse()

        assert len(parsed_items) == 1
        assert parsed_items[0].price_markup == markup_case.get("price_with_markup")
        assert 1 == parsed_items[0].title.count("Triangle")
