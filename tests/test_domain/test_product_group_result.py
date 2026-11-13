"""Контракт типизированных пакетов и общего доступа к результатам групп."""

from collections.abc import Callable
from dataclasses import FrozenInstanceError
from typing import Literal, assert_type

import pytest

from domain.battery.result import BatteryResult
from domain.product_group_result import ProductGroupResult, ProductPosition, TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem


def test_empty_package_keeps_group() -> None:
    """Выбранная пустая группа сохраняет идентичность без фиктивной позиции."""
    package = TireAndDiskResult()

    assert_type(package.product_group, Literal[ProductGroup.TIRE_AND_DISK])
    assert package.product_group is ProductGroup.TIRE_AND_DISK
    assert package.positions == ()


def test_package_preserves_model_and_order() -> None:
    """Конкретный пакет сохраняет тип, порядок и сами доменные позиции."""
    rows = (RowItem({'title': 'Первая'}), RowItem({'title': 'Вторая'}))
    package = TireAndDiskResult(rows)

    assert_type(package.positions, tuple[RowItem, ...])
    assert package.positions is rows
    assert [row.identity.title for row in package.positions] == ['Первая', 'Вторая']


def _common_positions(package: ProductGroupResult[ProductPosition]) -> tuple[ProductPosition, ...]:
    """Общий контейнер не обещает шинные поля каждой позиции."""
    assert package.product_group is ProductGroup.TIRE_AND_DISK
    return package.positions


def test_common_view_preserves_positions_without_tire_fields() -> None:
    """Mypy проверяет ковариантность пакета и ограниченный тип общего доступа."""
    row = RowItem()
    positions = _common_positions(TireAndDiskResult((row,)))

    assert_type(positions, tuple[ProductPosition, ...])
    assert positions == (row,)
    assert positions[0].product_group is ProductGroup.TIRE_AND_DISK


@pytest.mark.parametrize(
    'positions',
    [
        pytest.param((object(),), id='foreign-model'),
        pytest.param((RowItem(), object()), id='mixed-models'),
        pytest.param([], id='mutable-container'),
    ],
)
def test_package_rejects_invalid_runtime_input(positions: object) -> None:
    """Нетипизированный вызывающий код также не может смешать модели или менять состав."""
    constructor: Callable[..., TireAndDiskResult] = TireAndDiskResult
    with pytest.raises(TypeError) as exc_info:
        constructor(positions)

    expected = (
        'Пакет tire_and_disk принимает только RowItem'
        if isinstance(positions, tuple)
        else 'Позиции пакета должны быть кортежем'
    )
    assert str(exc_info.value) == expected


def test_merge_rejects_battery_package_with_exact_reason() -> None:
    with pytest.raises(TypeError) as exc_info:
        TireAndDiskResult().merge(BatteryResult())

    assert str(exc_info.value) == 'Пакет tire_and_disk объединяется только с той же моделью'


@pytest.mark.parametrize('attribute', ['positions', 'product_group'])
def test_package_identity_and_membership_are_immutable(attribute: str) -> None:
    """После создания нельзя подменить состав пакета или его товарную группу."""
    package = TireAndDiskResult()

    with pytest.raises(FrozenInstanceError):
        setattr(package, attribute, ())


def test_group_cannot_be_supplied_separately() -> None:
    """Даже пустой пакет нельзя объявить аккумуляторным через аргумент конструктора."""
    constructor: Callable[..., TireAndDiskResult] = TireAndDiskResult

    with pytest.raises(TypeError):
        constructor(product_group=ProductGroup.BATTERIES)
