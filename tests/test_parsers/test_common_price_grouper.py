"""tests for CommonPriceGrouper."""

from typing import Any

import pytest

from parsers.common_price_grouper import CommonPriceGrouper
from parsers.row_item.row_item import RowItem

_PRICE_LOW = 10
_PRICE_MID = 15
_PRICE_HIGH = 20
_FIRST_ORDER = 1
_SECOND_ORDER = 2
_THIRD_ORDER = 3
_FROZEN_ORDER = "99"


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


def test_grouper() -> None:
    """Дубли разных поставщиков: TL в title / КАМА-NU 701 и NU701 / brand == manufacturer."""
    item_zapaska = _row(
        brand="НКШЗ",
        model="NU701",
        title="315/80R22.5 КАМА NU701 156/150K TL НКШЗ",
        supplier_name="Запаска (шины)",
        price_markup=_PRICE_LOW,
    )
    item_mim = _row(
        model="КАМА-NU 701",
        title="315/80R22.5 НКШЗ КАМА-NU 701 Универсальная 156/150K",
        intimacy="",
        supplier_name="Мим",
        price_markup=_PRICE_HIGH,
    )

    doubles = CommonPriceGrouper([item_zapaska, item_mim]).get_double_row_items()

    assert doubles == [item_zapaska, item_mim]
    assert item_zapaska.group_by_params == 1
    assert item_mim.group_by_params == 1
    assert int(item_zapaska.order) == _FIRST_ORDER
    assert int(item_mim.order) == _SECOND_ORDER
    assert item_zapaska.double_candidate
    assert not item_zapaska.is_double
    assert item_mim.is_double
    assert not item_mim.double_candidate


def test_single_item_is_not_double() -> None:
    price_row = _row()
    grouper = CommonPriceGrouper([price_row])

    assert grouper.get_double_row_items() == []
    assert not price_row.is_double
    assert not price_row.double_candidate
    assert int(price_row.order) == _FIRST_ORDER
    assert price_row.group_by_params == 1


def test_cheapest_of_three_is_double_candidate() -> None:
    expensive = _row(price_markup=_PRICE_HIGH)
    cheap = _row(price_markup=_PRICE_LOW)
    mid = _row(price_markup=_PRICE_MID)

    doubles = CommonPriceGrouper([expensive, cheap, mid]).get_double_row_items()

    assert doubles == [expensive, cheap, mid]
    assert cheap.double_candidate
    assert not cheap.is_double
    assert expensive.is_double
    assert mid.is_double
    assert int(expensive.order) == _FIRST_ORDER
    assert int(cheap.order) == _SECOND_ORDER
    assert int(mid.order) == _THIRD_ORDER


def test_distinct_keys_get_separate_groups() -> None:
    wide = _row(width="315")
    narrow = _row(width="205")

    grouper = CommonPriceGrouper([wide, narrow])
    grouped_rows = grouper.get_row_items()

    assert grouped_rows == [narrow, wide]
    assert narrow.group_by_params == 1
    assert wide.group_by_params == 2
    assert not wide.is_double
    assert not narrow.is_double
    assert grouper.get_double_row_items() == []


def test_group_by_params_does_not_regroup() -> None:
    grouper = CommonPriceGrouper([_row(), _row(price_markup=_PRICE_HIGH)])
    grouped = grouper.group_by_params()
    price_row = grouper.row_items[0]
    price_row.order = _FROZEN_ORDER

    assert grouper.group_by_params() is grouped
    assert grouper.get_row_items() is grouper.row_items
    assert str(price_row.order) == _FROZEN_ORDER


def test_get_row_items_triggers_grouping() -> None:
    price_row = _row()
    grouped_rows = CommonPriceGrouper([price_row]).get_row_items()

    assert grouped_rows == [price_row]
    assert price_row.group_by_params == 1
    assert int(price_row.order) == _FIRST_ORDER


def test_passenger_tl_in_title_matches_without_tl() -> None:
    """Форточки с TL в title и позиция без TL — одна группа."""
    with_tl = _row(
        type_production="легковая",
        diameter="16",
        width="205",
        model="Snow Cross 2",
        title="205/55R16 Snow Cross 2 TL",
        supplier_name="Форточки",
        price_markup=_PRICE_LOW,
    )
    without_tl = _row(
        type_production="легковая",
        diameter="16",
        width="205",
        model="SNOW CROSS 2",
        title="205/55R16 SNOW CROSS 2",
        intimacy="",
        supplier_name="Мим",
        price_markup=_PRICE_HIGH,
    )

    doubles = CommonPriceGrouper([with_tl, without_tl]).get_double_row_items()

    assert doubles == [with_tl, without_tl]
    assert with_tl.group_by_params == without_tl.group_by_params


def test_axis_does_not_split_group() -> None:
    """Мим с осью склеивается с позицией без оси."""
    with_axis = _row(axis="Рулевая", supplier_name="Мим", price_markup=_PRICE_HIGH)
    without_axis = _row(supplier_name="Запаска", price_markup=_PRICE_LOW)

    doubles = CommonPriceGrouper([with_axis, without_axis]).get_double_row_items()

    assert doubles == [with_axis, without_axis]
    assert with_axis.group_by_params == without_axis.group_by_params


def test_explicit_tt_does_not_match_tl() -> None:
    tube_type = _row(title="315/80R22.5 NU701 TT", intimacy="", price_markup=_PRICE_LOW)
    tubeless = _row(title="315/80R22.5 NU701 TL", price_markup=_PRICE_HIGH)

    grouper = CommonPriceGrouper([tube_type, tubeless])

    assert grouper.get_double_row_items() == []
    assert tube_type.group_by_params != tubeless.group_by_params


def test_pw1_does_not_match_ps1() -> None:
    pw_item = _row(model="PW-1")
    ps_item = _row(model="PS-1")

    assert CommonPriceGrouper([pw_item, ps_item]).get_double_row_items() == []


def test_blank_tubes_not_doubles() -> None:
    first = _empty_identity(type_production="камера", price_markup=_PRICE_LOW)
    second = _empty_identity(type_production="камера", price_markup=_PRICE_HIGH)

    assert CommonPriceGrouper([first, second]).get_double_row_items() == []
    assert not first.is_double
    assert not first.double_candidate
    assert not second.is_double
    assert not second.double_candidate


def test_blank_tires_not_doubles() -> None:
    first = _empty_identity(price_markup=_PRICE_LOW)
    second = _empty_identity(price_markup=_PRICE_HIGH)

    assert CommonPriceGrouper([first, second]).get_double_row_items() == []


def test_filled_identity_still_duplicates() -> None:
    cheap = _row(price_markup=_PRICE_LOW)
    expensive = _row(price_markup=_PRICE_HIGH)

    doubles = CommonPriceGrouper([cheap, expensive]).get_double_row_items()

    assert doubles == [cheap, expensive]
    assert cheap.double_candidate
    assert expensive.is_double


_KAMA_ALIASES = {
    "НКШЗ": ["НК.ШЗ", "Нк.шз", "Кама", "Kama"],
    "Triangle": [],
}


def test_nkshz_and_kama_same_size_are_doubles() -> None:
    zapaska = _row(
        manufacturer_name="НКШЗ",
        model="NU701",
        title="315/80R22.5 Кама NU701 156/150K TL НкШЗ",
        supplier_name="Запаска (шины)",
        price_markup=_PRICE_LOW,
    )
    mim = _row(
        manufacturer_name="Кама",
        model="NU 701",
        title="315/80R22.5 Кама NU 701",
        supplier_name="Мим",
        price_markup=_PRICE_HIGH,
    )

    doubles = CommonPriceGrouper([zapaska, mim], _KAMA_ALIASES).get_double_row_items()

    assert doubles == [zapaska, mim]
    assert zapaska.group_by_params == mim.group_by_params


def test_nkshz_and_triangle_are_not_doubles() -> None:
    nkshz = _row(manufacturer_name="НКШЗ")
    triangle = _row(manufacturer_name="Triangle")

    grouper = CommonPriceGrouper([nkshz, triangle], _KAMA_ALIASES)

    assert grouper.get_double_row_items() == []
    assert nkshz.group_by_params != triangle.group_by_params


def test_comma_diameter_still_duplicates() -> None:
    comma = _row(diameter="22,5")
    dot = _row(diameter="22.5", price_markup=_PRICE_HIGH)

    doubles = CommonPriceGrouper([comma, dot]).get_double_row_items()

    assert doubles == [comma, dot]
    assert comma.group_by_params == dot.group_by_params


def test_r_prefix_diameter_still_duplicates() -> None:
    prefixed = _row(diameter="R22.5")
    plain = _row(diameter="22.5", price_markup=_PRICE_HIGH)

    doubles = CommonPriceGrouper([prefixed, plain]).get_double_row_items()

    assert doubles == [prefixed, plain]
    assert prefixed.group_by_params == plain.group_by_params


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
    item_35 = _row(title="35X12.50R17 Maxxis Trepador", **shared)
    item_33 = _row(
        title="33X12.50R17 Maxxis Trepador",
        price_markup=_PRICE_HIGH,
        **shared,
    )

    grouper = CommonPriceGrouper([item_35, item_33])

    assert grouper.get_double_row_items() == []
    assert item_35.group_by_params != item_33.group_by_params


@pytest.mark.parametrize(
    ("field", "left", "right"),
    [
        ("pcd1", 108, 114.3),
        ("eet", 40, 50),
        ("slot_count", 4, 5),
        ("central_diameter", 66.6, 67.1),
        ("color", "BKF", "S"),
    ],
)
def test_filled_disk_fields_split_groups(field: str, left: Any, right: Any) -> None:
    first = _disk_row(**{field: left})
    second = _disk_row(**{field: right}, price_markup=_PRICE_HIGH)
    grouper = CommonPriceGrouper([first, second])

    assert grouper.get_double_row_items() == []
    assert first.group_by_params != second.group_by_params


@pytest.mark.parametrize(
    ("field", "filled"),
    [
        ("pcd1", 108),
        ("eet", 40),
        ("slot_count", 5),
        ("central_diameter", 66.6),
        ("color", "BKF"),
    ],
)
def test_empty_disk_field_matches_filled(field: str, filled: Any) -> None:
    blank = _disk_row()
    with_value = _disk_row(**{field: filled}, price_markup=_PRICE_HIGH)
    doubles = CommonPriceGrouper([blank, with_value]).get_double_row_items()

    assert doubles == [blank, with_value]
    assert blank.group_by_params == with_value.group_by_params


def test_empty_pcd1_does_not_glue_distinct_values() -> None:
    pcd_108 = _disk_row(pcd1=108)
    pcd_114 = _disk_row(pcd1=114.3, price_markup=_PRICE_MID)
    blank = _disk_row(price_markup=_PRICE_HIGH)
    grouper = CommonPriceGrouper([pcd_108, pcd_114, blank])

    assert grouper.get_double_row_items() == []
    assert len({pcd_108.group_by_params, pcd_114.group_by_params, blank.group_by_params}) == 3


def test_zepp_factory_and_valve_are_not_doubles() -> None:
    shared = {
        "model": "10/335/281/175",
        "width": "9.0",
        "diameter": "22.5",
        "manufacturer_name": "ZEPP",
        "disk_thickness": "16",
    }
    canon = "9.0x22.5 10x335 ET175 281 Sil Zepp 10/335/281/175 (16 мм) б/к"
    yz = _disk_row(**shared, title=f"{canon} (YZ)", price_markup=_PRICE_LOW)
    hap_outer = _disk_row(
        **shared,
        title=f"{canon} (HAP) alive наруж. вентиль",
        price_markup=_PRICE_MID,
    )
    hap_inner = _disk_row(
        **shared,
        title=f"{canon} (HAP) внутр. вентиль",
        price_markup=_PRICE_HIGH,
    )
    grouper = CommonPriceGrouper([yz, hap_outer, hap_inner])

    assert grouper.get_double_row_items() == []
    assert len({yz.group_by_params, hap_outer.group_by_params, hap_inner.group_by_params}) == 3


def test_spike_in_title_still_duplicates() -> None:
    with_word = _row(title="315/80R22.5 NU701 шип")
    plain = _row(price_markup=_PRICE_HIGH)
    doubles = CommonPriceGrouper([with_word, plain]).get_double_row_items()

    assert doubles == [with_word, plain]
    assert not with_word.disputed
    assert not plain.disputed


def test_explicit_spike_yes_no_is_disputed() -> None:
    yes_spike = _row(spike="Да")
    no_spike = _row(spike="Нет", price_markup=_PRICE_HIGH)
    doubles = CommonPriceGrouper([yes_spike, no_spike]).get_double_row_items()

    assert doubles == [yes_spike, no_spike]
    assert yes_spike.disputed == "шип"
    assert no_spike.disputed == "шип"


def test_empty_spike_is_not_disputed() -> None:
    yes_spike = _row(spike="Да")
    blank = _row(price_markup=_PRICE_HIGH)
    doubles = CommonPriceGrouper([yes_spike, blank]).get_double_row_items()

    assert doubles == [yes_spike, blank]
    assert not yes_spike.disputed
    assert not blank.disputed


def test_explicit_season_conflict_is_disputed() -> None:
    winter = _row(season="Зимняя")
    summer = _row(season="Летняя", price_markup=_PRICE_HIGH)
    doubles = CommonPriceGrouper([winter, summer]).get_double_row_items()

    assert doubles == [winter, summer]
    assert winter.disputed == "сезон"
    assert summer.disputed == "сезон"


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("зима", "зимняя"),
        ("ЗИМА", "Зимняя"),
        ("лето", "летняя"),
        ("ЛЕТО", "Летняя"),
    ],
)
def test_season_aliases_are_not_disputed(left: str, right: str) -> None:
    first = _row(season=left)
    second = _row(season=right, price_markup=_PRICE_HIGH)
    doubles = CommonPriceGrouper([first, second]).get_double_row_items()

    assert doubles == [first, second]
    assert not first.disputed
    assert not second.disputed


def test_short_season_aliases_still_conflict() -> None:
    winter = _row(season="зима")
    summer = _row(season="лето", price_markup=_PRICE_HIGH)
    doubles = CommonPriceGrouper([winter, summer]).get_double_row_items()

    assert doubles == [winter, summer]
    assert winter.disputed == "сезон"
    assert summer.disputed == "сезон"


@pytest.mark.parametrize(
    ("left", "right"),
    [
        ("да", "yes"),
        ("Да", "YES"),
        ("да", "ш."),
        ("нет", "no"),
        ("Нет", "NO"),
    ],
)
def test_spike_aliases_are_not_disputed(left: str, right: str) -> None:
    first = _row(spike=left)
    second = _row(spike=right, price_markup=_PRICE_HIGH)
    doubles = CommonPriceGrouper([first, second]).get_double_row_items()

    assert doubles == [first, second]
    assert not first.disputed
    assert not second.disputed


def test_spike_yes_and_no_aliases_are_disputed() -> None:
    yes_spike = _row(spike="yes")
    no_spike = _row(spike="no", price_markup=_PRICE_HIGH)
    doubles = CommonPriceGrouper([yes_spike, no_spike]).get_double_row_items()

    assert doubles == [yes_spike, no_spike]
    assert yes_spike.disputed == "шип"
    assert no_spike.disputed == "шип"
