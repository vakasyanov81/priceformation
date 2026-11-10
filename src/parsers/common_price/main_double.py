"""Главный дубль группы — строка, которую общая логика отбора оставила бы в шаблоне."""

from domain.row_item.row_item import RowItem
from parsers.common_price.double_selection import pick_double
from parsers.common_price.warehouses import merge_warehouse_rows


def main_double(row_items: list[RowItem], priority_suppliers: tuple[str, ...] = ()) -> RowItem:
    """Главный дубль группы.

    Склады одной группы сначала сводятся, как для drom, затем применяется общая
    логика ``pick_double``: остаток → приоритетный поставщик → наличие → не уценка →
    свежесть партии → цена.
    """
    return pick_double(merge_warehouse_rows(row_items), priority_suppliers)


# Дубль, чья цена отличается от цены главного дубля на эту долю и больше, считается сомнительным.
_DOUBTFUL_PRICE_DEVIATION = 0.05


def is_doubtful_price(row_item: RowItem, main_item: RowItem) -> bool:
    """Закупочная цена дубля отклоняется от закупочной цены главного дубля на 5% и более (в любую сторону)."""
    main_price = main_item.pricing.price_opt
    if not main_price:
        return False
    return abs(row_item.pricing.price_opt - main_price) / main_price >= _DOUBTFUL_PRICE_DEVIATION
