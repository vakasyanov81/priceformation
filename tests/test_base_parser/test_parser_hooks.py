"""Default vendor-row pipeline after enrich."""

from test_parsers.test_vendors.parse_config import make_parse_configuration

from parsers.base_parser.base_parser import BaseParser, make_parser
from parsers.base_parser.base_parser_config import ParseConfiguration
from parsers.base_parser.markup_policy import IdentityMarkupPolicy
from parsers.row_item.row_item import RowItem
from parsers.vendors.pioner import pioner_params

_OPT = 100
_REST_OK = 10
_REST_LOW = 1
_CATEGORY = "Диск"


_CALLS: list[str] = []


class _OrderParser(BaseParser):
    def after_row_mapped(self, row_item: RowItem) -> None:
        _CALLS.append("after")

    def skip_by_min_rest(self, row_item: RowItem) -> None:
        _CALLS.append("skip")
        super().skip_by_min_rest(row_item)

    def category_for(self, row_item: RowItem) -> str | None:
        _CALLS.append("category")
        return _CATEGORY

    def add_price_markup(self, row_item: RowItem) -> None:
        _CALLS.append("markup")
        super().add_price_markup(row_item)


def _parser() -> _OrderParser:
    parse_config = ParseConfiguration(make_parse_configuration(pioner_params))
    _CALLS.clear()
    return make_parser(
        _OrderParser,
        parse_config,
        markup_policy=IdentityMarkupPolicy.create(),
    )


def test_default_row_pipeline_order() -> None:
    parser = _parser()
    row = RowItem({"price_opt": _OPT, "rest_count": _REST_OK})
    parser.process_parsed_row(row)
    assert _CALLS == ["after", "skip", "category", "markup"]
    assert row.type_production == _CATEGORY
    assert row.price_markup == _OPT


def test_skip_zeroes_low_rest() -> None:
    parser = _parser()
    row = RowItem({"price_opt": _OPT, "rest_count": _REST_LOW})
    parser.process_parsed_row(row)
    assert row.to_dict().get("rest_count") == 0


def test_skip_none_rest_zeroes_count() -> None:
    parser = _parser()
    row = RowItem({"price_opt": _OPT})
    parser.process_parsed_row(row)
    assert row.to_dict().get("rest_count") == 0


def test_category_for_none_keeps_type() -> None:
    parse_config = ParseConfiguration(make_parse_configuration(pioner_params))
    parser = make_parser(
        BaseParser,
        parse_config,
        markup_policy=IdentityMarkupPolicy.create(),
    )
    row = RowItem({"price_opt": _OPT, "rest_count": _REST_OK, "type_production": _CATEGORY})
    parser.process_parsed_row(row)
    assert row.type_production == _CATEGORY
