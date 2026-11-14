"""Пакет аккумуляторов не позволяет смешать модели или потерять группу."""

from collections.abc import Callable
from dataclasses import FrozenInstanceError
from typing import Literal, assert_type

import pytest

from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from domain.product_group_result import ProductGroupResult, ProductPosition, TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from services.parse_result import ParseResult


def test_empty_and_nonempty_packages_preserve_battery_identity() -> None:
    first = BatteryItem.from_fields({'code': '01'})
    second = BatteryItem.from_fields({'code': '02'})
    original = BatteryResult((first,))
    merged = original.merge(BatteryResult((second,)))

    assert_type(merged.positions, tuple[BatteryItem, ...])
    assert_type(merged.product_group, Literal[ProductGroup.BATTERIES])
    assert BatteryResult().product_group is ProductGroup.BATTERIES
    assert merged.positions == (first, second)
    assert original.positions == (first,)
    assert original.merge(BatteryResult()) == original


def test_common_result_keeps_real_models_separate() -> None:
    battery = BatteryItem()
    tire = RowItem()
    battery_package: ProductGroupResult[ProductPosition] = BatteryResult((battery,))
    parse_result = ParseResult()
    parse_result.add_package(battery_package)
    parse_result.add_package(TireAndDiskResult((tire,)))

    assert parse_result.groups[ProductGroup.BATTERIES].positions == (battery,)
    assert parse_result.tire_and_disk_items == [tire]


@pytest.mark.parametrize(
    'positions',
    [
        pytest.param([]),
        pytest.param((object(),)),
        pytest.param((RowItem(),)),
        pytest.param((BatteryItem(), RowItem())),
    ],
)
def test_foreign_or_mutable_input_is_rejected(positions: object) -> None:
    constructor: Callable[..., BatteryResult] = BatteryResult
    with pytest.raises(TypeError) as exc_info:
        constructor(positions)

    expected = (
        'Пакет batteries принимает только BatteryItem'
        if isinstance(positions, tuple)
        else 'Позиции пакета должны быть кортежем'
    )
    assert str(exc_info.value) == expected


def test_merge_rejects_tire_package() -> None:
    with pytest.raises(TypeError) as exc_info:
        BatteryResult().merge(TireAndDiskResult())

    assert str(exc_info.value) == 'Пакет batteries объединяется только с той же моделью'


@pytest.mark.parametrize('attribute', ['product_group', 'positions'])
def test_result_membership_is_immutable(attribute: str) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(BatteryResult(), attribute, ())
