"""
tests for Pioner vendor after raw-parser process
"""

from typing import Any

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
from parsers.data_provider.markup_rules import MarkupRulesProviderBase
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.pioner import PionerParser, pioner_params

parser_config = make_parse_configuration(pioner_params, markup_rules=PionerMarkupRulesProviderForTests())


def get_fake_parser(parse_result: Any) -> PionerParser:
    """get fake parser"""
    FakeXlsReader.parse_result = next(iter(parse_result.values()))
    return PionerParser(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


class TestParsePioner:
    """
    tests for Pioner vendor after raw-parser process
    """

    def test_parse(self) -> None:
        """check all field for one price-row"""

        parsed_items: list[RowItem] = get_fake_parser(pioner_one_item_result()).parse()

        assert len(parsed_items) == 1
        assert parsed_items[0].title == "Автокамера 14.00-24"
        assert parsed_items[0].price_markup == 2310
        assert parsed_items[0].supplier_name == "Пионер"
        assert parsed_items[0].percent_markup == 5

    def test_parse_brand(self) -> None:
        """check all field for one price-row"""

        parsed_items: list[RowItem] = get_fake_parser(pioner_one_item_result_with_categories()).parse()

        assert len(parsed_items) == 1
        assert parsed_items[0].brand == "triangle"

    def test_small_rest(self) -> None:
        """test exclude price-position with small rest count"""
        parse_result = pioner_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["rest_count"] = 3

        parsed_items: list[RowItem] = get_fake_parser(parse_result).parse()

        assert len(parsed_items) == 0

    @pytest.mark.parametrize("price_opt", [0, None])
    def test_null_price_opt(self, price_opt: Any) -> None:
        """test exclude price-position with null price purchase"""
        parse_result = pioner_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["price_opt"] = price_opt

        parsed_items: list[RowItem] = get_fake_parser(parse_result).parse()

        assert len(parsed_items) == 0

    def test_small_rest_1(self) -> None:
        """test exclude price-position with small rest count"""
        parse_result = pioner_one_item_result()
        first_row = get_first_row_item(parse_result)
        first_row["rest_count"] = 10
        first_row["reserve_count"] = 7

        parsed_items: list[RowItem] = get_fake_parser(parse_result).parse()

        assert len(parsed_items) == 0

    @pytest.mark.parametrize(
        "markup_case",
        [
            {
                "price": 150000,
                "price_with_markup": 157500,
                "category": "автошины TRIANGLE",
            },
        ],
    )
    def test_markup(self, markup_case: Any) -> None:
        """test markup"""
        parse_result = pioner_one_item_result_with_categories()
        rows = get_rows(parse_result)
        rows[1]["title"] = markup_case.get("category")
        rows[2]["price_opt"] = markup_case.get("price")
        rows[2]["price_recommended"] = markup_case.get("price_recommended")

        parsed_items: list[RowItem] = get_fake_parser(parse_result).parse()

        assert len(parsed_items) == 1
        assert parsed_items[0].price_markup == markup_case.get("price_with_markup")
        assert parsed_items[0].title.count("Triangle") == 1


@pytest.mark.parametrize(
    ("price_opt", "percent"),
    [
        (1000, 0.20),
        (1001, 0.18),
        (2000, 0.18),
    ],
)
def test_markup_percent_includes_rule_min(price_opt: float, percent: float) -> None:
    parser = get_fake_parser(pioner_one_item_result())
    assert parser.get_markup_percent(price_opt) == percent


class _EmptyMarkupRules(MarkupRulesProviderBase):
    def get_markup_data(self) -> dict[str, Any]:
        return {"markup_rules": {}}


def _parser_with_markup(markup: MarkupRulesProviderBase) -> PionerParser:
    FakeXlsReader.parse_result = next(iter(pioner_one_item_result().values()))
    return PionerParser(
        xls_reader=FakeXlsReader,
        file_prices=list(pioner_one_item_result().keys()),
        parse_config=ParseConfiguration(make_parse_configuration(pioner_params, markup_rules=markup)),
    )


def test_prochie_category_zeroes_rest() -> None:
    parse_result = {
        "file_prices\\pioner\\price.xls": [
            {"title": "Прочие"},
            {
                "title": "Автокамера 14.00-24",
                "price_opt": "2200,0 Руб.",
                "rest_count": 20.0,
                "reserve_count": "",
            },
        ]
    }
    assert get_fake_parser(parse_result).parse() == []


def test_item_rest_missing_is_zero() -> None:
    assert PionerParser.get_item_rest(RowItem({})) == 0
    assert PionerParser.get_item_rest(RowItem({"rest_count": 10, "reserve_count": 3})) == 7


def test_add_price_markup_without_opt_stays_zero() -> None:
    parser = get_fake_parser(pioner_one_item_result())
    row = RowItem({})
    parser.add_price_markup(row)
    assert row.price_markup == 0


def test_add_price_markup_empty_rules_keeps_opt() -> None:
    parser = _parser_with_markup(_EmptyMarkupRules())
    row = RowItem({"price_opt": 1000})
    parser.add_price_markup(row)
    assert row.price_markup == 1000
    assert row.percent_markup == 0
