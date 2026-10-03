"""Группировка строк прайса по параметрам наименования."""

from functools import partial
from itertools import groupby
from operator import attrgetter
from typing import Any

from domain.row_item.row_item import RowItem
from parsers.common_price_dispute import dispute_note
from parsers.common_price_group_key import clear_model, group_key
from parsers.common_price_size import canon_number, size_fields
from parsers.data_provider.manufacturer_aliases import load_aliases_map

_MIN_ITEMS_FOR_DOUBLES = 2
_GROUP_ORDER_KEY = attrgetter('duplicate.group_by_params', 'duplicate.order')


def _has_product_identity(row_item: RowItem) -> bool:
    """Есть размер или модель — позицию можно искать среди дублей."""
    if any(size_fields(row_item)):
        return True
    return bool(clear_model(row_item.identity.model, row_item.identity.manufacturer, row_item.identity.brand))


def _mark_double_items(row_items: list[RowItem]) -> None:
    """Проставить признаки дублей внутри одной группы."""
    if len(row_items) < _MIN_ITEMS_FOR_DOUBLES:
        return

    min_price_item = min(row_items, key=lambda row_item: row_item.pricing.price_markup)
    dispute = dispute_note(row_items)

    for row_item in row_items:
        if row_item.duplicate.order == min_price_item.duplicate.order:
            row_item.set_field('double_candidate', True)
        else:
            row_item.set_field('is_double', True)
        if dispute:
            row_item.set_field('disputed', dispute)


def _optional_disk_parts(row_item: RowItem) -> tuple[str, ...]:
    """ET/PCD/цвет: пустое — wildcard, заполненное сравниваем жёстко."""
    return (
        canon_number(row_item.disk.slot_count),
        canon_number(row_item.disk.pcd1),
        canon_number(row_item.disk.eet),
        canon_number(row_item.disk.central_diameter),
        (row_item.disk.color or '').strip().lower(),
    )


def _split_group_by_index(group: list[RowItem], index: int) -> list[list[RowItem]]:
    """Разные заполненные значения поля режут группу; пустые остаются вместе."""
    filled: dict[str, list[RowItem]] = {}
    empties: list[RowItem] = []
    for row_item in group:
        field_value = _optional_disk_parts(row_item)[index]
        if field_value:
            filled.setdefault(field_value, []).append(row_item)
        else:
            empties.append(row_item)
    if len(filled) <= 1:
        return [group]
    parts = list(filled.values())
    if empties:
        parts.append(empties)
    return parts


def _split_optional_disk(row_items: list[RowItem]) -> list[list[RowItem]]:
    """После ядра ключа разрезать по опциональным полям диска."""
    groups = [row_items]
    field_count = len(_optional_disk_parts(row_items[0]))
    for index in range(field_count):
        groups = [part for group in groups for part in _split_group_by_index(group, index)]
    return groups


def _apply_split_groups(
    grouper: CommonPriceGrouper,
    start_id: int,
    row_items: list[RowItem],
) -> int:
    """Выдать подгруппы ядра и вернуть следующий group_id."""
    group_id = start_id
    for subgroup in _split_optional_disk(row_items):
        group_id += 1
        grouper._apply_group(group_id, subgroup)
    return group_id


class CommonPriceGrouper:
    """Группировка результата разбора прайсов поставщиков по параметрам наименований"""

    def __init__(self, row_items: list[RowItem], aliases_map: dict[str, Any] | None = None):
        self.row_items = row_items
        self._aliases_map = load_aliases_map() if aliases_map is None else aliases_map
        self._is_grouped = False

    def group_by_params(self) -> CommonPriceGrouper:
        """Группировка списка по параметрам и разметка дублей."""
        if self._is_grouped:
            return self

        self._assign_orders()
        self._assign_groups()
        self.row_items.sort(key=_GROUP_ORDER_KEY)
        self._is_grouped = True
        return self

    def _assign_orders(self) -> None:
        """Проставить исходный порядок (O(N))."""
        for idx, row_item in enumerate(self.row_items, start=1):
            row_item.set_field('order', idx)

    def _assign_groups(self) -> None:
        """Сгруппировать, разметить дубли и выставить group_by_params."""
        group_id = 0
        item_key = partial(group_key, aliases_map=self._aliases_map)
        sorted_items = sorted(self.row_items, key=item_key)
        for _key, group_iter in groupby(sorted_items, key=item_key):
            group_id = _apply_split_groups(self, group_id, list(group_iter))

    def _apply_group(self, group_id: int, group_items: list[RowItem]) -> None:
        """Обработать одну группу дублей."""
        if _has_product_identity(group_items[0]):
            _mark_double_items(group_items)
        for row_item in group_items:
            row_item.set_field('group_by_params', group_id)

    def get_row_items(self) -> list[RowItem]:
        """Получить сгруппированные позиции."""
        if not self._is_grouped:
            self.group_by_params()
        return self.row_items

    def get_double_row_items(self) -> list[RowItem]:
        """Получить список дублей."""
        if not self._is_grouped:
            self.group_by_params()
        return [
            row_item
            for row_item in self.row_items
            if row_item.duplicate.is_double or row_item.duplicate.double_candidate
        ]
