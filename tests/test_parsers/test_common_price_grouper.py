"""tests for CommonPriceGrouper."""

from typing import Any
from unittest.mock import patch

import pytest

from parsers.common_price_grouper import CommonPriceGrouper
from parsers.row_item.row_item import RowItem

_PRICE_LOW = 10
_PRICE_MID = 15
_PRICE_HIGH = 20
_FIRST_ORDER = 1
_FROZEN_ORDER = "99"
_KAMA_ALIASES = {
    "НКШЗ": ["НК.ШЗ", "Нк.шз", "Кама", "Kama"],
    "Triangle": [],
}
_ZEPP_CANON = "9.0x22.5 10x335 ET175 281 Sil Zepp 10/335/281/175 (16 мм) б/к"
_DISK_SPLIT = (
    ("pcd1", 108, 114.3),
    ("eet", 40, 50),
    ("slot_count", 4, 5),
    ("central_diameter", 66.6, 67.1),
    ("color", "BKF", "S"),
)
_DISK_FILLED = (
    ("pcd1", 108),
    ("eet", 40),
    ("slot_count", 5),
    ("central_diameter", 66.6),
    ("color", "BKF"),
)


def _row(**fields: Any) -> RowItem:
    payload: dict[str, Any] = {
        "width": "315",
        "model": "NU701",
        "diameter": "22.5",
        "height_percent": "80",
        "index_load": "156/150",
        "index_velocity": "K",
        "title": "315/80R22.5 NU701 156/150K",
        "type_production": "Грузовая шина",
        "manufacturer_name": "НКШЗ",
        "price_markup": _PRICE_LOW,
    }
    payload.update(fields)
    return RowItem(payload)


def _empty_identity(**fields: Any) -> RowItem:
    payload: dict[str, Any] = {
        "type_production": "легковая",
        "manufacturer_name": "GreenStone",
        "width": "",
        "diameter": "",
        "model": "",
        "price_markup": _PRICE_LOW,
    }
    payload.update(fields)
    return RowItem(payload)


def _disk_row(**fields: Any) -> RowItem:
    payload: dict[str, Any] = {
        "width": "7.0",
        "diameter": "17",
        "model": "Rebel",
        "title": "7.0x17 Rebel",
        "type_production": "диск",
        "manufacturer_name": "LS",
        "price_markup": _PRICE_LOW,
        "height_percent": "",
        "index_load": "",
        "index_velocity": "",
    }
    payload.update(fields)
    return RowItem(payload)


def _high(**fields: Any) -> RowItem:
    return _row(price_markup=_PRICE_HIGH, **fields)


def _disk_high(**fields: Any) -> RowItem:
    return _disk_row(price_markup=_PRICE_HIGH, **fields)


def _zepp(title: str, **fields: Any) -> RowItem:
    return _disk_row(
        model="10/335/281/175",
        width="9.0",
        diameter="22.5",
        manufacturer_name="ZEPP",
        disk_thickness="16",
        title=title,
        **fields,
    )


def _doubles(*rows: RowItem, aliases: dict[str, Any] | None = None) -> list[RowItem]:
    return CommonPriceGrouper(list(rows), aliases).get_double_row_items()


def _assert_grouped(
    *rows: RowItem,
    aliases: dict[str, Any] | None = None,
    disputed: str = "",
) -> None:
    assert _doubles(*rows, aliases=aliases) == list(rows)
    assert len({row.group_by_params for row in rows}) == 1
    assert all((row.disputed or "") == disputed for row in rows)


def _assert_split(*rows: RowItem, aliases: dict[str, Any] | None = None) -> None:
    assert _doubles(*rows, aliases=aliases) == []
    assert len({row.group_by_params for row in rows}) == len(rows)


def _assert_flags(candidate: RowItem, *others: RowItem) -> None:
    assert candidate.double_candidate and not candidate.is_double
    assert all(other.is_double and not other.double_candidate for other in others)


def _assert_orders(*rows: RowItem) -> None:
    for expected, row in enumerate(rows, start=_FIRST_ORDER):
        assert int(row.order) == expected


def test_grouper() -> None:
    """Дубли разных поставщиков: TL в title / КАМА-NU 701 и NU701 / brand == manufacturer."""
    item_zapaska = _row(
        brand="НКШЗ",
        title="315/80R22.5 КАМА NU701 156/150K TL НКШЗ",
        supplier_name="Запаска (шины)",
    )
    item_mim = _high(
        model="КАМА-NU 701",
        title="315/80R22.5 НКШЗ КАМА-NU 701 Универсальная 156/150K",
        intimacy="",
        supplier_name="Мим",
    )
    _assert_grouped(item_zapaska, item_mim)
    _assert_flags(item_zapaska, item_mim)
    _assert_orders(item_zapaska, item_mim)


def test_grouper_loads_aliases_once_when_omitted() -> None:
    """без aliases_map grouper читает карту один раз, не на каждую строку"""
    with patch("parsers.common_price_grouper.load_aliases_map", return_value={}) as mock_load:
        CommonPriceGrouper([_row(), _high()]).group_by_params()
    mock_load.assert_called_once()


def test_single_item_is_not_double() -> None:
    price_row = _row()
    assert _doubles(price_row) == []
    assert not (price_row.is_double or price_row.double_candidate)
    _assert_orders(price_row)
    assert price_row.group_by_params == 1


def test_cheapest_of_three_is_double_candidate() -> None:
    expensive = _high()
    cheap = _row()
    mid = _row(price_markup=_PRICE_MID)
    _assert_grouped(expensive, cheap, mid)
    _assert_flags(cheap, expensive, mid)
    _assert_orders(expensive, cheap, mid)


def test_distinct_keys_get_separate_groups() -> None:
    wide = _row()
    narrow = _row(width="205")
    grouper = CommonPriceGrouper([wide, narrow])
    assert grouper.get_row_items() == [narrow, wide]
    assert (narrow.group_by_params, wide.group_by_params) == (1, 2)
    assert grouper.get_double_row_items() == []


def test_group_by_params_does_not_regroup() -> None:
    grouper = CommonPriceGrouper([_row(), _high()])
    grouped = grouper.group_by_params()
    price_row = grouper.row_items[0]
    price_row.order = _FROZEN_ORDER
    assert grouper.group_by_params() is grouped
    assert grouper.get_row_items() is grouper.row_items
    assert str(price_row.order) == _FROZEN_ORDER


def test_get_row_items_triggers_grouping() -> None:
    price_row = _row()
    assert CommonPriceGrouper([price_row]).get_row_items() == [price_row]
    assert price_row.group_by_params == 1
    _assert_orders(price_row)


def test_passenger_tl_in_title_matches_without_tl() -> None:
    """Форточки с TL в title и позиция без TL — одна группа."""
    shared = {"type_production": "легковая", "diameter": "16", "width": "205"}
    with_tl = _row(
        **shared,
        model="Snow Cross 2",
        title="205/55R16 Snow Cross 2 TL",
        supplier_name="Форточки",
    )
    without_tl = _high(
        **shared,
        model="SNOW CROSS 2",
        title="205/55R16 SNOW CROSS 2",
        intimacy="",
        supplier_name="Мим",
    )
    _assert_grouped(with_tl, without_tl)


def test_axis_does_not_split_group() -> None:
    """Мим с осью склеивается с позицией без оси."""
    _assert_grouped(_high(axis="Рулевая", supplier_name="Мим"), _row(supplier_name="Запаска"))


def test_explicit_tt_does_not_match_tl() -> None:
    _assert_split(_row(title="315/80R22.5 NU701 TT", intimacy=""), _high(title="315/80R22.5 NU701 TL"))


def test_pw1_does_not_match_ps1() -> None:
    _assert_split(_row(model="PW-1"), _row(model="PS-1"))


@pytest.mark.parametrize("type_production", ["камера", "легковая"])
def test_blank_identity_not_doubles(type_production: str) -> None:
    first = _empty_identity(type_production=type_production)
    second = _empty_identity(type_production=type_production, price_markup=_PRICE_HIGH)
    assert _doubles(first, second) == []
    assert not any(row.is_double or row.double_candidate for row in (first, second))


def test_filled_identity_still_duplicates() -> None:
    cheap, expensive = _row(), _high()
    _assert_grouped(cheap, expensive)
    _assert_flags(cheap, expensive)


def test_nkshz_and_kama_same_size_are_doubles() -> None:
    zapaska = _row(title="315/80R22.5 Кама NU701 156/150K TL НкШЗ", supplier_name="Запаска (шины)")
    mim = _high(manufacturer_name="Кама", model="NU 701", title="315/80R22.5 Кама NU 701", supplier_name="Мим")
    _assert_grouped(zapaska, mim, aliases=_KAMA_ALIASES)


def test_nkshz_and_triangle_are_not_doubles() -> None:
    _assert_split(_row(), _row(manufacturer_name="Triangle"), aliases=_KAMA_ALIASES)


@pytest.mark.parametrize("diameter", ["22,5", "R22.5"])
def test_normalized_diameter_still_duplicates(diameter: str) -> None:
    _assert_grouped(_row(diameter=diameter), _high())


def test_inch_outer_diameters_are_not_doubles() -> None:
    shared = {
        "model": "Trepador",
        "width": "12.50",
        "diameter": "17",
        "height_percent": "",
        "manufacturer_name": "Maxxis",
        "index_load": "",
        "index_velocity": "",
        "type_production": "легковая",
    }
    _assert_split(
        _row(title="35X12.50R17 Maxxis Trepador", **shared),
        _high(title="33X12.50R17 Maxxis Trepador", **shared),
    )


@pytest.mark.parametrize(("field", "left", "right"), _DISK_SPLIT)
def test_filled_disk_fields_split_groups(field: str, left: Any, right: Any) -> None:
    first = _disk_row(**{field: left})
    second = _disk_high(**{field: right})
    _assert_split(first, second)


@pytest.mark.parametrize(("field", "filled"), _DISK_FILLED)
def test_empty_disk_field_matches_filled(field: str, filled: Any) -> None:
    _assert_grouped(_disk_row(), _disk_high(**{field: filled}))


def test_empty_pcd1_does_not_glue_distinct_values() -> None:
    _assert_split(
        _disk_row(pcd1=108),
        _disk_row(pcd1=114.3, price_markup=_PRICE_MID),
        _disk_high(),
    )


def test_zepp_factory_and_valve_are_not_doubles() -> None:
    _assert_split(
        _zepp(f"{_ZEPP_CANON} (YZ)"),
        _zepp(f"{_ZEPP_CANON} (HAP) alive наруж. вентиль", price_markup=_PRICE_MID),
        _zepp(f"{_ZEPP_CANON} (HAP) внутр. вентиль", price_markup=_PRICE_HIGH),
    )


@pytest.mark.parametrize(
    ("left_fields", "right_fields", "note"),
    [
        ({"spike": "Да"}, {"spike": "Нет"}, "шип"),
        ({"spike": "yes"}, {"spike": "no"}, "шип"),
        ({"season": "Зимняя"}, {"season": "Летняя"}, "сезон"),
        ({"season": "зима"}, {"season": "лето"}, "сезон"),
    ],
)
def test_explicit_conflict_is_disputed(
    left_fields: dict[str, str],
    right_fields: dict[str, str],
    note: str,
) -> None:
    _assert_grouped(_row(**left_fields), _high(**right_fields), disputed=note)


@pytest.mark.parametrize(
    ("left_fields", "right_fields"),
    [
        ({"season": "зима"}, {"season": "зимняя"}),
        ({"season": "ЗИМА"}, {"season": "Зимняя"}),
        ({"season": "лето"}, {"season": "летняя"}),
        ({"season": "ЛЕТО"}, {"season": "Летняя"}),
        ({"spike": "да"}, {"spike": "yes"}),
        ({"spike": "Да"}, {"spike": "YES"}),
        ({"spike": "да"}, {"spike": "ш."}),
        ({"spike": "нет"}, {"spike": "no"}),
        ({"spike": "Нет"}, {"spike": "NO"}),
        ({"title": "315/80R22.5 NU701 шип"}, {}),
        ({"spike": "Да"}, {}),
    ],
)
def test_same_group_not_disputed(left_fields: dict[str, str], right_fields: dict[str, str]) -> None:
    _assert_grouped(_row(**left_fields), _high(**right_fields))
