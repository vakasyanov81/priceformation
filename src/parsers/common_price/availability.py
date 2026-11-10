"""Признак «под заказ» по колонке «Наличие»: общий для выбора дубля и главного дубля."""

from domain.row_item.row_item import RowItem

_ON_ORDER_MARKER = 'заказ'


def is_on_order(row_item: RowItem) -> bool:
    """Под заказ — в «Наличии» поставщика есть слово «заказ»; пусто — в наличии."""
    return _ON_ORDER_MARKER in (row_item.stock.available or '').lower()
