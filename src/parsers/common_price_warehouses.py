"""Объединение складов одной группы в прайсе для дрома."""

from copy import deepcopy

from domain.row_item.row_item import RowItem

type _MergeKey = tuple[str, str, str]


def merge_warehouse_rows(row_items: list[RowItem]) -> list[RowItem]:
    """Склады одной группы — одна строка на позицию поставщика.

    Строки с одинаковой наименьшей ценой складываются по остаткам; строки с более
    высокой ценой не учитываются. Новые объекты — исходные позиции не меняются
    (их пишет и свой прайс). Порядок строк сохраняется.
    """
    buckets: dict[_MergeKey, list[RowItem]] = {}
    for row_item in row_items:
        key = _merge_key(row_item)
        if key is not None:
            buckets.setdefault(key, []).append(row_item)

    merged: list[RowItem] = []
    emitted: set[_MergeKey] = set()
    for row_item in row_items:
        key = _merge_key(row_item)
        if key is None:
            merged.append(row_item)
        elif key not in emitted:
            emitted.add(key)
            merged.append(cheapest_with_summed_rest(buckets[key]))
    return merged


def _merge_key(row_item: RowItem) -> _MergeKey | None:
    """Поставщик, код позиции и группа склада; склад без группы не объединяем."""
    group = row_item.stock.warehouse_group
    code = row_item.identity.code
    if not group or not code:
        return None
    return row_item.vendor.supplier_name or '', code, group


def cheapest_with_summed_rest(rows: list[RowItem]) -> RowItem:
    """Строка с наименьшей ценой; при равной наименьшей цене остатки складываются в копию."""
    if len(rows) == 1:
        return rows[0]
    cheapest_price = min(row.pricing.price_markup for row in rows)
    cheapest = [row for row in rows if row.pricing.price_markup == cheapest_price]
    total_rest = sum(row.stock.rest_count or 0 for row in cheapest)
    merged = deepcopy(cheapest[0])
    merged.set_field('rest_count', total_rest)
    return merged
