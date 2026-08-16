"""tests for Autosnab54 vendor: size/model from title."""

from typing import Any

import pytest
from test_base_parser.test_manufacturer_finder import map_manufacturer
from test_parsers.test_vendors.test_parse_poshk import (
    BlackListProviderForTests,
    MarkupRulesProviderForTests,
    StopWordsProviderForTests,
    VendorListProviderForTests,
)

from parsers import data_provider
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
)
from parsers.common_price_grouper import CommonPriceGrouper
from parsers.fake_xls_reader import FakeXlsReader
from parsers.row_item.row_item import RowItem
from parsers.vendors.autosnab54_ru import Autosnab54Parser, autosnab_params
from parsers.vendors.autosnab_title import fill_from_title

_PRICE_AUTOSNAB = 21200
_PRICE_OTHER = 22000
_REST_COUNT = 10

_VENDOR_LIST = {"autosnab54_ru": {"enabled": 1}}


class _AutosnabAliases(data_provider.ManufacturerAliasesProviderBase):
    def get_aliases(self) -> dict[str, Any]:
        aliases = dict(map_manufacturer)
        aliases["GreenStone"] = ()
        aliases["Sailun"] = ()
        return aliases


parser_config = BasePriceParseConfigurationParams(
    black_list_provider=BlackListProviderForTests(),
    markup_rules_provider=MarkupRulesProviderForTests(),
    stop_words_provider=StopWordsProviderForTests(),
    vendor_list=VendorListProviderForTests(_VENDOR_LIST),
    manufacturer_aliases=_AutosnabAliases(),
    parser_params=autosnab_params,
)


def _as_parse_result(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {"file_prices/autosnab54_ru/price.xls": rows}


def _fake_parser(parse_result: Any) -> Autosnab54Parser:
    FakeXlsReader.parse_result = list(parse_result.values())[0]
    return Autosnab54Parser(
        xls_reader=FakeXlsReader,
        file_prices=list(parse_result.keys()),
        parse_config=ParseConfiguration(parser_config),
    )


def _raw_row(**fields: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type_production": "Грузовая шина",
        "manufacturer_name": "GREENSTONE",
        "title": "11R22.5 GREENSTONE DR55 16PR 146/143K ведущая ось",
        "season": "Всесезонная",
        "spike": "",
        "price_opt": _PRICE_AUTOSNAB,
        "rest_count": _REST_COUNT,
    }
    payload.update(fields)
    return payload


def _fill(title: str, manufacturer: str = "") -> RowItem:
    row_item = RowItem({"title": title, "manufacturer_name": manufacturer})
    fill_from_title(row_item)
    return row_item


@pytest.mark.parametrize(
    ("title", "manufacturer", "width", "height", "diameter", "model"),
    [
        (
            "11R22.5 GREENSTONE DR55 16PR 146/143K ведущая ось",
            "GreenStone",
            "11",
            None,
            "22.5",
            "DR55",
        ),
        (
            "12.00R24  GREENSTONE DR899 20PR 160/157K карьер",
            "GreenStone",
            "12.00",
            None,
            "24",
            "DR899",
        ),
        (
            "7.00R16C GREENSTONE ST896 14PR 118/114L",
            "GreenStone",
            "7.00",
            None,
            "16",
            "ST896",
        ),
        (
            "175/65R14 Viatti Brina V-521 82T",
            "Viatti",
            "175",
            "65",
            "14",
            "Brina V-521",
        ),
        (
            "195/75R16C DoubleStar DW01 96/93Q",
            "Doublestar",
            "195",
            "75",
            "16",
            "DW01",
        ),
        (
            "205/55R16 Triangle Touring ReliaX TE307 91V TL",
            "Triangle",
            "205",
            "55",
            "16",
            "Touring ReliaX TE307",
        ),
        (
            "215/75R17.5 Triangle TR689A 135/133L 16PR TL ведущая",
            "Triangle",
            "215",
            "75",
            "17.5",
            "TR689A",
        ),
        (
            "235/55R17 Nordman 8 SUV 103T",
            "Nordman",
            "235",
            "55",
            "17",
            "8 SUV",
        ),
        (
            "255/55R19 Triangle PL01 3PMSF M+S 111R XL TL",
            "Triangle",
            "255",
            "55",
            "19",
            "PL01",
        ),
        (
            "265/70R16 Sailun Ice Blazer WST3 TL 112T шип",
            "Sailun",
            "265",
            "70",
            "16",
            "Ice Blazer WST3",
        ),
        (
            "295/80R22.5 Blackhawk (Sailun Group Co., LTD) BDR75 TL M+S 3PMSF 152/149M 18PR",
            "Blackhawk",
            "295",
            "80",
            "22.5",
            "BDR75",
        ),
        (
            "205/55ZR16 Triangle TE307 91V",
            "Triangle",
            "205",
            "55",
            "16",
            "TE307",
        ),
        (
            "31x10.5R15 Crossleader DSU02 92Y",
            "Crossleader",
            "10.5",
            None,
            "15",
            "DSU02",
        ),
    ],
)
def test_fill_from_title_size_and_model(
    title: str,
    manufacturer: str,
    width: str,
    height: str | None,
    diameter: str,
    model: str,
) -> None:
    row_item = _fill(title, manufacturer)
    assert row_item.width == width
    assert row_item.height_percent == height
    assert row_item.diameter == diameter
    assert row_item.model == model


@pytest.mark.parametrize(
    "title",
    [
        "Камера 1220x400-533 (425/85R21) НкШЗ",
        "Камера СВК 11.00-20 ГК-145",
        "без размера GreenStone DR55",
        "",
    ],
)
def test_fill_from_title_skips_unparsed(title: str) -> None:
    row_item = _fill(title, "GreenStone")
    assert not row_item.width
    assert not row_item.height_percent
    assert not row_item.diameter
    assert not row_item.model


def test_unknown_brand_stays_in_model() -> None:
    row_item = _fill("11R22.5 GREENSTONE DR55 16PR", "Viatti")
    assert row_item.model == "GREENSTONE DR55"


def test_fill_from_title_inch_sets_ext_diameter() -> None:
    row_item = _fill("31x10.5R15 Crossleader DSU02 92Y", "Crossleader")
    assert row_item.ext_diameter == 31


def test_partial_brand_not_stripped() -> None:
    row_item = _fill("11R22.5 GreenStone DR55 16PR", "Green")
    assert row_item.model == "GreenStone DR55"


def test_fill_from_title_strips_brand_field() -> None:
    row_item = RowItem(
        {
            "title": "11R22.5 GREENSTONE DR55 16PR 146/143K",
            "brand": "GREENSTONE",
        },
    )
    fill_from_title(row_item)
    assert row_item.model == "DR55"


def test_fill_from_title_keeps_existing_fields() -> None:
    row_item = RowItem(
        {
            "title": "215/75R17.5 Triangle TR689A 135/133L",
            "width": "999",
            "height_percent": "1",
            "diameter": "10",
            "model": "KEEP",
        },
    )
    fill_from_title(row_item)
    assert row_item.width == "999"
    assert row_item.height_percent == "1"
    assert row_item.diameter == "10"
    assert row_item.model == "KEEP"


def test_parse_greenstone_and_passenger() -> None:
    rows = [
        _raw_row(),
        _raw_row(
            type_production="Легковая шина",
            manufacturer_name="Viatti",
            title="175/65R14 Viatti Brina V-521 82T",
            season="Зимняя",
            price_opt=3600,
            rest_count=16,
        ),
    ]
    parsed = _fake_parser(_as_parse_result(rows)).parse()
    assert len(parsed) == 2

    truck = parsed[0]
    assert truck.manufacturer == "GreenStone"
    assert truck.width == "11"
    assert not truck.height_percent
    assert truck.diameter == "22.5"
    assert truck.model == "DR55"
    assert truck.price_markup == _PRICE_AUTOSNAB
    assert truck.supplier_name == "Автоснабжение"

    passenger = parsed[1]
    assert passenger.manufacturer == "Viatti"
    assert passenger.width == "175"
    assert passenger.height_percent == "65"
    assert passenger.diameter == "14"
    assert passenger.model == "Brina V-521"


def test_greenstone_different_sizes_not_grouped() -> None:
    parsed = _fake_parser(
        _as_parse_result(
            [
                _raw_row(title="11R22.5 GREENSTONE DR668 16PR 146/143L ведущая ось"),
                _raw_row(
                    title="295/80R22.5 GREENSTONE DR668 18PR 152/149L ведущая ось",
                    price_opt=_PRICE_OTHER,
                ),
            ],
        ),
    ).parse()
    grouped = CommonPriceGrouper(parsed, aliases_map={"GreenStone": []}).get_double_row_items()
    assert grouped == []
    assert parsed[0].width != parsed[1].width
    assert parsed[0].model == parsed[1].model == "DR668"


def test_matching_model_joins_cross_vendor_group() -> None:
    autosnab = _fake_parser(
        _as_parse_result(
            [
                _raw_row(
                    manufacturer_name="Triangle",
                    title="215/75R17.5 Triangle TR689A 135/133L 16PR TL ведущая",
                ),
            ],
        ),
    ).parse()[0]
    other = RowItem(
        {
            "type_production": "Грузовая шина",
            "manufacturer_name": "Triangle",
            "model": "TR689A",
            "width": "215",
            "height_percent": "75",
            "diameter": "17.5",
            "title": "215/75R17.5 Triangle TR689A 135/133L",
            "price_markup": _PRICE_OTHER,
            "supplier_name": "Мим",
        },
    )
    doubles = CommonPriceGrouper(
        [autosnab, other],
        aliases_map={"Triangle": []},
    ).get_double_row_items()
    assert len(doubles) == 2
    assert {price_row.supplier_name for price_row in doubles} == {"Автоснабжение", "Мим"}
