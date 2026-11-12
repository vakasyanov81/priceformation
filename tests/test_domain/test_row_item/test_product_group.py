"""Принадлежность существующей модели группе шин и дисков."""

from typing import Literal, assert_type

import pytest

from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem


@pytest.mark.parametrize('category', ['', 'Автошина', 'Диск', 'Камера', 'Ободная лента'])
def test_category_does_not_change_product_group(category: str) -> None:
    """Категории внутри шинной модели не являются отдельными товарными группами."""
    row = RowItem({'type_production': category})

    assert_type(row.product_group, Literal[ProductGroup.TIRE_AND_DISK])
    assert row.product_group is ProductGroup.TIRE_AND_DISK

    row.set_field('type_production', 'Аккумулятор')

    assert row.product_group is ProductGroup.TIRE_AND_DISK


def test_product_group_does_not_extend_serialized_fields() -> None:
    """Принадлежность модели не добавляет колонку в существующие машинные форматы."""
    row = RowItem({'title': '  Шина  ', 'price_opt': '1 500,50', 'rest_count': '4'})
    expected = [('title', 'Шина'), ('price_opt', 1500.5), ('rest_count', 4)]

    assert row.product_group is ProductGroup.TIRE_AND_DISK
    assert list(row.to_dict().items()) == expected
    assert RowItem().to_dict() == {}
