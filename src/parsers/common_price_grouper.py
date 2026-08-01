"""Группировка строк прайса по параметрам наименования."""

from itertools import groupby
from typing import List

from parsers.common_price_group_key import group_key
from parsers.row_item.row_item import RowItem


def _mark_double_items(row_items: List[RowItem]) -> None:
    """Проставить признаки дублей внутри одной группы."""
    if len(row_items) < 2:
        return

    min_price_item = min(row_items, key=lambda row_item: row_item.price_markup)

    for row_item in row_items:
        if row_item.order == min_price_item.order:
            row_item.double_candidate = True
        else:
            row_item.is_double = True


class CommonPriceGrouper:
    """Группировка результата разбора прайсов поставщиков по параметрам наименований"""

    def __init__(self, row_items: List[RowItem]):
        self.row_items = row_items
        self._is_grouped = False

    def group_by_params(self) -> "CommonPriceGrouper":
        """Группировка списка по параметрам и разметка дублей."""
        if self._is_grouped:
            return self

        self._assign_orders()
        self._assign_groups()
        self.row_items.sort(key=lambda grouped: (grouped.group_by_params, grouped.order))
        self._is_grouped = True
        return self

    def _assign_orders(self) -> None:
        """Проставить исходный порядок (O(N))."""
        for idx, row_item in enumerate(self.row_items, start=1):
            row_item.order = idx

    def _assign_groups(self) -> None:
        """Сгруппировать, разметить дубли и выставить group_by_params."""
        group_id = 0
        sorted_items = sorted(self.row_items, key=group_key)
        for _key, group_iter in groupby(sorted_items, key=group_key):
            group_id += 1
            self._apply_group(group_id, list(group_iter))

    def _apply_group(self, group_id: int, group_items: List[RowItem]) -> None:
        """Обработать одну группу дублей."""
        _mark_double_items(group_items)
        for row_item in group_items:
            row_item.group_by_params = group_id

    def get_row_items(self) -> List[RowItem]:
        """Получить сгруппированные позиции."""
        if not self._is_grouped:
            self.group_by_params()
        return self.row_items

    def get_double_row_items(self) -> List[RowItem]:
        """Получить список дублей."""
        if not self._is_grouped:
            self.group_by_params()
        return [
            row_item
            for row_item in self.row_items
            if getattr(row_item, "is_double", False) or getattr(row_item, "double_candidate", False)
        ]
