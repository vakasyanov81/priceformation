"""tests for category correction, title strip and purchase-price filter."""

from test_parsers.test_vendors.parse_config import make_parse_configuration

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.base_parser_row import drop_empty_rest
from parsers.base_parser.category_finder import CategoryFinder
from parsers.row_item.row_item import RowItem
from parsers.vendors.pioner import pioner_params

_TITLE = "ok title"
_REST = 5
_PRICE = 100


def _parser() -> BaseParser:
    return BaseParser(parse_config=ParseConfiguration(make_parse_configuration(pioner_params)))


def _parser_with_finder() -> BaseParser:
    parser = _parser()
    parser._category_finder = CategoryFinder()  # noqa: WPS437
    return parser


def test_correction_category_skips_without_finder() -> None:
    parser = _parser()
    row = RowItem({"type_production": "грузовая"})
    parser.correction_category(row)
    assert row.type_production == "грузовая"


def test_correction_category_skips_empty_type() -> None:
    parser = _parser_with_finder()
    row = RowItem({})
    parser.correction_category(row)
    assert not row.type_production


def test_correction_category_maps_alias() -> None:
    parser = _parser_with_finder()
    row = RowItem({"type_production": "грузовая"})
    parser.correction_category(row)
    assert row.type_production == "Грузовая шина"


def test_strip_words_collapses_spaces() -> None:
    assert BaseParser.strip_words_in_title("  385/65   R22.5  ") == "385/65 R22.5"


def test_strip_words_keeps_empty_and_whitespace() -> None:
    assert BaseParser.strip_words_in_title("") == ""
    assert BaseParser.strip_words_in_title("   ") == "   "


def test_drop_row_with_rest_and_no_purchase_price() -> None:
    parser = _parser()
    dropped = RowItem({"title": _TITLE, "rest_count": _REST})
    kept = RowItem({"title": _TITLE, "rest_count": _REST, "price_opt": _PRICE})
    assert parser.filter_keep([dropped, kept]) == [kept]


def test_drop_empty_rest_requires_opt_and_rest() -> None:
    kept = RowItem({"title": _TITLE, "rest_count": _REST, "price_opt": _PRICE})
    no_rest = RowItem({"title": _TITLE, "price_opt": _PRICE})
    no_opt = RowItem({"title": _TITLE, "rest_count": _REST})
    zero_rest = RowItem({"title": _TITLE, "rest_count": 0, "price_opt": _PRICE})
    assert drop_empty_rest([kept, no_rest, no_opt, zero_rest]) == [kept]
