"""Признак «под заказ» и срок доставки из названия склада («НС.Под заказ от 4д.»)."""

import re

from domain.row_item.row_item import RowItem

ORDER_AVAILABLE = 'Под заказ'
_ORDER_MARKER = re.compile(r'под\s+заказ', re.IGNORECASE)
_DELIVERY_DAYS = re.compile(r'\bот\s*(\d+)\s*д', re.IGNORECASE)


def apply_warehouse_order(row_item: RowItem) -> None:
    """Склад «под заказ»: наличие «Под заказ» и срок доставки в днях, если он указан в названии."""
    name = row_item.stock.warehouse_name or ''
    if not _ORDER_MARKER.search(name):
        return
    row_item.set_field('available', ORDER_AVAILABLE)
    days = _DELIVERY_DAYS.search(name)
    if days is not None:
        row_item.set_field('delivery_period', int(days.group(1)))
