"""Отбор позиций: склады, минимальный остаток."""

from domain.row_item.row_item import RowItem
from parsers.base_parser.row_processor import apply_min_rest
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.base_parser.warehouse_order import apply_warehouse_order

DEFAULT_MIN_REST = 4


def drop_empty_rest(row_items: list[RowItem]) -> list[RowItem]:
    """Оставить позиции с ценой закупки и остатком.

    rest_count может быть ``>40`` и не приводится к float — только истинность.
    """
    return [row_item for row_item in row_items if row_item.pricing.price_opt and row_item.stock.rest_count]


class RowFilters:
    """Фильтры позиций и правила остатка; поведение задают `StrategyHooks` (без них — дефолты)."""

    def __init__(self, hooks: StrategyHooks | None = None) -> None:
        self._hooks = hooks

    def filter_warehouses(self, row_items: list[RowItem]) -> list[RowItem]:
        """Отбросить позиции складов вне выбранных городов (`behavior.warehouse_cities`) до дорогого разбора."""
        if self._hooks is None or self._hooks.warehouse_filter is None:
            return row_items
        city_filter = self._hooks.warehouse_filter
        return [row_item for row_item in row_items if city_filter.allows(row_item)]

    def apply_warehouse_order(self, row_item: RowItem) -> None:
        """Наличие «Под заказ» и срок доставки из названия склада (`behavior.order_from_warehouse_name`)."""
        if self._hooks is not None and self._hooks.order_from_warehouse_name:
            apply_warehouse_order(row_item)

    def skip_by_min_rest(self, row_item: RowItem) -> None:
        """Отсечь по мин. остатку: стратегия или дефолт."""
        if self._hooks is not None and self._hooks.rest is not None:
            rest = self._hooks.rest.item_rest(row_item)
            min_rest = self._hooks.min_rest
        else:
            rest = row_item.stock.rest_count
            min_rest = DEFAULT_MIN_REST
        apply_min_rest(row_item, rest, min_rest)
