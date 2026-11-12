"""Связь типов позиции, обработчика, пакета и выходных полей."""

from collections.abc import Sequence
from typing import assert_type

import pytest

from domain.product_group_handler import InputFields, OutputFields, ProductGroupHandler
from domain.product_group_result import ProductGroupResult, ProductPosition
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from tests.test_domain.group_handler_examples import OtherHandlerExample, TestPosition, TireHandlerExample


def _run_handler[TPosition: ProductPosition](
    group_handler: ProductGroupHandler[TPosition],
    rows: Sequence[InputFields],
) -> ProductGroupResult[TPosition]:
    """Общий вызывающий код не знает полей модели и конкретного класса пакета."""
    positions = [group_handler.create_position(row) for row in rows]
    processed = group_handler.process(positions)
    assert processed.product_group is group_handler.product_group
    return group_handler.group(processed)


def test_tire_handler_preserves_row_item_type() -> None:
    """Текущая модель использует интерфейс без изменения её полей и преобразований."""
    group_handler: ProductGroupHandler[RowItem] = TireHandlerExample()
    package = _run_handler(group_handler, [{'title': '  Шина  ', 'price_opt': '1 500,50'}])

    assert_type(package, ProductGroupResult[RowItem])
    assert_type(package.positions[0], RowItem)
    assert package.positions[0].identity.title == 'Шина'
    assert package.positions[0].pricing.price_opt == 1500.5
    assert group_handler.prepare_output(package) == ({'title': 'Шина', 'price': 1500.5},)


def test_other_model_needs_no_tire_fields() -> None:
    """Тот же общий код сохраняет другую модель вплоть до явного преобразования вывода."""
    group_handler: ProductGroupHandler[TestPosition] = OtherHandlerExample()
    package = _run_handler(group_handler, [{'label': 'Произвольная позиция'}])

    assert_type(package, ProductGroupResult[TestPosition])
    assert_type(package.positions[0], TestPosition)
    assert package.product_group is ProductGroup.BATTERIES
    assert package.positions[0].label == 'Произвольная позиция'
    output = group_handler.prepare_output(package)
    assert_type(output, tuple[OutputFields, ...])
    assert output == ({'label': 'Произвольная позиция'},)


def _empty_output[TPosition: ProductPosition](
    group_handler: ProductGroupHandler[TPosition],
) -> tuple[OutputFields, ...]:
    """Пустая выбранная группа проходит все операции, сохраняя идентификатор."""
    package = _run_handler(group_handler, [])
    assert package.product_group is group_handler.product_group
    assert package.positions == ()
    return group_handler.prepare_output(package)


def test_empty_groups_keep_identity() -> None:
    """Для пустого пакета не требуется угадывать группу по первой позиции."""
    assert _empty_output(TireHandlerExample()) == ()
    assert _empty_output(OtherHandlerExample()) == ()


def test_creation_error_reaches_caller() -> None:
    """Общий код не подменяет ошибку модели пустым успешным результатом."""
    with pytest.raises(TypeError, match='метка'):
        _run_handler(OtherHandlerExample(), [{'label': 12}])
