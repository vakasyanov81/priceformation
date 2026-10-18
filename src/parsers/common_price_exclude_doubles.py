"""Исключение дублей в шаблоне: из группы дублей остаётся одна строка.

Порядок выбора внутри группы (``group_by_params``):

0. строки без остатка не выбираются, пока в группе есть строка с остатком;
1. приоритетный поставщик (``priority_suppliers`` в ``doubles.json``, по порядку списка);
2. в наличии важнее, чем под заказ: под заказ игнорируется, если есть позиция в наличии;
3. наименьшая цена с наценкой; при равной цене остатки таких строк складываются.
"""

from collections.abc import Callable

from domain.row_item.row_item import RowItem
from parsers.common_price_warehouses import cheapest_with_summed_rest

_ON_ORDER_MARKER = 'заказ'

type _Narrow = Callable[[list[RowItem]], list[RowItem]]


def exclude_doubles(row_items: list[RowItem], priority_suppliers: tuple[str, ...] = ()) -> list[RowItem]:
    """Одна строка на группу дублей; строки вне групп дублей не меняются.

    Строка группы встаёт на место первой строки группы. Новые объекты при сложении
    остатков — исходные позиции не меняются (их пишут другие шаблоны).
    """
    groups: dict[int, list[RowItem]] = {}
    for row_item in row_items:
        group_id = _double_group(row_item)
        if group_id is not None:
            groups.setdefault(group_id, []).append(row_item)

    kept: list[RowItem] = []
    emitted: set[int] = set()
    for row_item in row_items:
        group_id = _double_group(row_item)
        if group_id is None:
            kept.append(row_item)
        elif group_id not in emitted:
            emitted.add(group_id)
            kept.append(pick_double(groups[group_id], priority_suppliers))
    return kept


def pick_double(rows: list[RowItem], priority_suppliers: tuple[str, ...] = ()) -> RowItem:
    """Строка группы дублей, которая остаётся в шаблоне."""
    narrows: tuple[_Narrow, ...] = (
        _with_rest,
        lambda candidates: _from_priority_supplier(candidates, priority_suppliers),
        _in_stock,
    )
    candidates = rows
    for narrow in narrows:
        candidates = narrow(candidates) or candidates
    return cheapest_with_summed_rest(candidates)


def is_on_order(row_item: RowItem) -> bool:
    """Под заказ — в «Наличии» поставщика есть слово «заказ»; пусто — в наличии."""
    return _ON_ORDER_MARKER in (row_item.stock.available or '').lower()


def _double_group(row_item: RowItem) -> int | None:
    duplicate = row_item.duplicate
    if not (duplicate.is_double or duplicate.double_candidate):
        return None
    return duplicate.group_by_params


def _with_rest(rows: list[RowItem]) -> list[RowItem]:
    return [row_item for row_item in rows if row_item.stock.rest_count]


def _from_priority_supplier(rows: list[RowItem], priority_suppliers: tuple[str, ...]) -> list[RowItem]:
    for supplier in priority_suppliers:
        matched = [row_item for row_item in rows if row_item.vendor.supplier_name == supplier]
        if matched:
            return matched
    return []


def _in_stock(rows: list[RowItem]) -> list[RowItem]:
    return [row_item for row_item in rows if not is_on_order(row_item)]
