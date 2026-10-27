"""Отбор позиций в BaseParser: склады, минимальный остаток, служебные строки."""

from domain.row_item.row_item import RowItem
from parsers.base_parser.parser_title import ParserTitle
from parsers.base_parser.row_processor import apply_min_rest
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.base_parser.warehouse_order import apply_warehouse_order


class ParserRows(ParserTitle):
    """Фильтры позиций и правила остатка."""

    def filter_warehouses(self, row_items: list[RowItem]) -> list[RowItem]:
        """Отбросить позиции складов вне выбранных городов (`behavior.warehouse_cities`) до дорогого разбора."""
        hooks = self._strategy_hooks
        if hooks is None or hooks.warehouse_filter is None:
            return row_items
        city_filter = hooks.warehouse_filter
        return [row_item for row_item in row_items if city_filter.allows(row_item)]

    @classmethod
    def apply_warehouse_order(cls, hooks: StrategyHooks, row_item: RowItem) -> None:
        """Наличие «Под заказ» и срок доставки из названия склада (`behavior.order_from_warehouse_name`)."""
        if hooks.order_from_warehouse_name:
            apply_warehouse_order(row_item)

    def skip_by_min_rest(self, row_item: RowItem) -> None:
        """Отсечь по мин. остатку: стратегия или дефолт."""
        if self._strategy_hooks and self._strategy_hooks.rest is not None:
            rest = self._strategy_hooks.rest.item_rest(row_item)
            min_rest = self._strategy_hooks.min_rest
        else:
            rest = self.get_item_rest(row_item)
            min_rest = self.get_min_rest_count()
        apply_min_rest(row_item, rest, min_rest)

    @classmethod
    def get_item_rest(cls, row_item: RowItem) -> int | None:
        return row_item.stock.rest_count

    @classmethod
    def get_min_rest_count(cls) -> int:
        return 4

    @classmethod
    def is_category_row(cls, row_item: RowItem) -> bool:
        return bool(row_item.identity.title and not row_item.pricing.price_opt)
