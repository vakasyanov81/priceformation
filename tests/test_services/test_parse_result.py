"""Контракт результата разбора, составленного из пакетов товарных групп."""

import pytest

from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from services.parse_result import ParseResult
from tests.test_domain.group_handler_examples import TestGroupResult, TestPosition


def test_absent_group_is_not_replaced_with_empty_package() -> None:
    """Невыбранная группа отсутствует, а не создаётся при обращении из старого writer."""
    parsed = ParseResult()

    assert parsed.groups == {}
    assert parsed.tire_and_disk_items == []
    assert parsed.groups == {}


def test_selected_empty_group_keeps_its_identity() -> None:
    """Выбранная группа с нулём позиций присутствует собственным пустым пакетом."""
    parsed = ParseResult()

    parsed.add_package(TireAndDiskResult())

    assert set(parsed.groups) == {ProductGroup.TIRE_AND_DISK}
    assert parsed.groups[ProductGroup.TIRE_AND_DISK].positions == ()


def test_packages_from_suppliers_merge_without_mutating_originals() -> None:
    """Позиции поставщиков одной группы объединяются в новый неизменяемый пакет."""
    first_row = RowItem({'title': 'Первая'})
    second_row = RowItem({'title': 'Вторая'})
    first = TireAndDiskResult((first_row,))
    second = TireAndDiskResult((second_row,))
    parsed = ParseResult()

    parsed.add_package(first)
    parsed.add_package(second)

    assert first.positions == (first_row,)
    assert second.positions == (second_row,)
    assert parsed.tire_and_disk_items == [first_row, second_row]


def test_different_group_models_remain_separate() -> None:
    """Общий контейнер объединяет пакеты, но не смешивает позиции разных моделей."""
    tire = RowItem({'title': 'Шина'})
    other = TestPosition('Другая модель')
    parsed = ParseResult()

    parsed.add_package(TireAndDiskResult((tire,)))
    parsed.add_package(TestGroupResult((other,)))

    assert parsed.tire_and_disk_items == [tire]
    assert parsed.groups[ProductGroup.BATTERIES].positions == (other,)


def test_package_rejects_merge_with_another_model() -> None:
    """Нетипизированный код не может объединить несовместимые доменные модели."""
    with pytest.raises(TypeError, match='той же моделью'):
        TireAndDiskResult().merge(TestGroupResult(()))
