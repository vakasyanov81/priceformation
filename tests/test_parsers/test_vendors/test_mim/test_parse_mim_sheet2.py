"""
tests for Mim vendor (sheet 2) after raw-parser process
"""

from typing import Any

import pytest
from test_parsers.fixtures.mim_sheet2 import mim_one_item_result
from test_parsers.test_vendors.test_parse_poshk import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    VendorListProviderForTests,
    vendor_list_config,
)

from parsers.base_parser.base_parser import make_parser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.mim.mim_2sheet import (
    TRUCK_TIRE_MARKUP_HIGH,
    TRUCK_TIRE_MARKUP_LOW,
    TRUCK_TIRE_PRICE_THRESHOLD,
    MimParser2Sheet,
    mim_sheet_2_params,
)

from ..parse_config import MimMarkupRulesProviderForTests

parser_config = BasePriceParseConfigurationParams(
    black_list_provider=BlackListProviderForTests(),
    markup_rules_provider=MimMarkupRulesProviderForTests(),
    vendor_list=VendorListProviderForTests(vendor_list_config),
    manufacturer_aliases=ManufacturerAliasesProviderForTests(),
    parser_params=mim_sheet_2_params,
)


def get_fake_parser(parse_result: Any) -> MimParser2Sheet:
    """get fake parser"""
    FakeXlsReader.parse_result = next(iter(parse_result.values()))
    return make_parser(
        MimParser2Sheet,
        ParseConfiguration(parser_config),
        file_prices=list(parse_result.keys()),
        data_reader=FakeXlsReader,
    )


def _title_parser() -> MimParser2Sheet:
    return MimParser2Sheet(parse_config=ParseConfiguration(parser_config))


def test_parse() -> None:
    """check all field for one price-row"""

    parsed_items: list[RowItem] = get_fake_parser(mim_one_item_result()).parse()

    assert len(parsed_items) == 1
    assert parsed_items[0].title == "295/75R22.5 Hifly HH312 PR16 146/143L TL Ведущая M+S"
    assert parsed_items[0].type_production == "Грузовая шина"
    assert parsed_items[0].price_markup == 24360.0
    assert parsed_items[0].supplier_name == "Мим"
    assert parsed_items[0].percent_markup == 5


def _sheet2_parser() -> MimParser2Sheet:
    return object.__new__(MimParser2Sheet)


@pytest.mark.parametrize(
    ("price_opt", "percent"),
    [
        (TRUCK_TIRE_PRICE_THRESHOLD, TRUCK_TIRE_MARKUP_LOW),
        (TRUCK_TIRE_PRICE_THRESHOLD + 1, TRUCK_TIRE_MARKUP_HIGH),
    ],
)
def test_truck_markup_percent(price_opt: float, percent: float) -> None:
    assert _sheet2_parser().get_markup_percent(price_opt) == percent


def test_markup_without_price_opt_is_zero() -> None:
    row = RowItem({})
    _sheet2_parser().add_price_markup(row)
    assert row.price_markup == 0


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        ({"width": "295", "diameter": "22.5"}, "295R22.5"),
        ({"width": "295", "height_percent": "75"}, "295/75"),
        ({"height_percent": "75", "diameter": "22.5"}, "/75R22.5"),
    ],
)
def test_prepared_title_skips_empty_parts(fields: dict[str, str], expected: str) -> None:
    assert _title_parser().get_prepared_title(RowItem(fields)) == expected
