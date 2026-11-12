"""Исключение дублей в шаблоне: из группы дублей остаётся одна строка.

Порядок выбора — общий с главным дублём (``double_selection.pick_double``):

0. строки без остатка не выбираются, пока в группе есть строка с остатком;
1. приоритетный поставщик (``priority_suppliers`` в ``doubles.json``, по порядку списка);
2. в наличии важнее, чем под заказ: под заказ игнорируется, если есть позиция в наличии;
3. уценка не выбирается, пока есть обычный товар;
4. из обычных выбирается самая свежая партия (без года — свежее любой даты);
5. наименьшая цена с наценкой; при равной цене остатки таких строк складываются.
"""

from domain.product_groups import DuplicateGroupKey
from domain.row_item.row_item import RowItem
from parsers.common_price.double_selection import pick_double


def exclude_doubles(row_items: list[RowItem], priority_suppliers: tuple[str, ...] = ()) -> list[RowItem]:
    """Одна строка на группу дублей; строки вне групп дублей не меняются.

    Строка группы встаёт на место первой строки группы. Новые объекты при сложении
    остатков — исходные позиции не меняются (их пишут другие шаблоны).
    """
    groups: dict[DuplicateGroupKey, list[RowItem]] = {}
    for row_item in row_items:
        group_id = _double_group(row_item)
        if group_id is not None:
            groups.setdefault(group_id, []).append(row_item)

    kept: list[RowItem] = []
    emitted: set[DuplicateGroupKey] = set()
    for row_item in row_items:
        group_id = _double_group(row_item)
        if group_id is None:
            kept.append(row_item)
        elif group_id not in emitted:
            emitted.add(group_id)
            kept.append(pick_double(groups[group_id], priority_suppliers))
    return kept


def _double_group(row_item: RowItem) -> DuplicateGroupKey | None:
    duplicate = row_item.duplicate
    if not (duplicate.is_double or duplicate.double_candidate) or duplicate.group_by_params is None:
        return None
    return DuplicateGroupKey(row_item.product_group, duplicate.group_by_params)
