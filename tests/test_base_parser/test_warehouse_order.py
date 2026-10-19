"""apply_warehouse_order: «под заказ» и срок доставки из названия склада."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.base_parser.warehouse_order import apply_warehouse_order


@pytest.mark.parametrize(
    ('warehouse', 'available', 'delivery_period'),
    [
        ('НС.Под заказ от 4д.', 'Под заказ', 4),
        ('МСК.ПОД  ЗАКАЗ от 12 дней', 'Под заказ', 12),
        ('НС.Под заказ', 'Под заказ', None),
        ('Двуречье', None, None),
        ('', None, None),
    ],
)
def test_order_from_warehouse_name(warehouse: str, available: str | None, delivery_period: int | None) -> None:
    row = RowItem({'rest_count': 5, 'warehouse_name': warehouse})

    apply_warehouse_order(row)

    assert (row.stock.available, row.stock.delivery_period) == (available, delivery_period)


def test_no_warehouse_name() -> None:
    row = RowItem({'rest_count': 5})

    apply_warehouse_order(row)

    assert (row.stock.available, row.stock.delivery_period) == (None, None)
