"""Общий выбор одной строки из группы дублей: остаток, поставщик, наличие, уценка, партия, цена.

Одна логика для отчёта (главный дубль) и для прайса (сейчас — drom), чтобы главный
дубль совпадал со строкой, которая уходит в шаблон.
"""

from collections.abc import Callable

from domain.row_item.row_item import RowItem
from parsers.common_price.availability import is_on_order
from parsers.common_price.warehouses import cheapest_with_summed_rest

# Позиция без года выпуска — считается свежей: поставщики пишут год только у старых партий.
_UNDATED = float('inf')

type _Narrow = Callable[[list[RowItem]], list[RowItem]]


def pick_double(rows: list[RowItem], priority_suppliers: tuple[str, ...] = ()) -> RowItem:
    """Строка группы дублей, которая остаётся в шаблоне."""
    narrows: tuple[_Narrow, ...] = (
        _with_rest,
        lambda candidates: _from_priority_supplier(candidates, priority_suppliers),
        _in_stock,
        _not_marked_down,
        _freshest,
    )
    candidates = rows
    for narrow in narrows:
        candidates = narrow(candidates) or candidates
    return cheapest_with_summed_rest(candidates)


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


def _not_marked_down(rows: list[RowItem]) -> list[RowItem]:
    return [row_item for row_item in rows if not row_item.stock.marked_down]


def _freshest(rows: list[RowItem]) -> list[RowItem]:
    freshest = max(_freshness(row_item) for row_item in rows)
    return [row_item for row_item in rows if _freshness(row_item) == freshest]


def _freshness(row_item: RowItem) -> float:
    return row_item.stock.production_year or _UNDATED
