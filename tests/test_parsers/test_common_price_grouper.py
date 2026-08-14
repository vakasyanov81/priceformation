"""tests for CommonPriceGrouper."""

from typing import Any

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


def test_grouper() -> None:
    """Дубли разных поставщиков: TL / модель после дефиса / brand == manufacturer."""
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
