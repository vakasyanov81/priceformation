"""Порядок строк в отчёте о дублях: группы с приоритетным поставщиком выше остальных."""

from domain.row_item.row_item import RowItem

_Ranks = dict[str, int]
_NONE = 10**6  # ранг «не приоритетный» для сравнения внутри min


def _group_of(row: RowItem) -> int:
    return row.duplicate.group_by_params or 0


def _supplier_rank(row: RowItem, rank: _Ranks) -> int:
    return rank.get(row.vendor.supplier_name or '', _NONE)


def _best_rank_by_group(rows: list[RowItem], rank: _Ranks) -> dict[int, int]:
    best: dict[int, int] = {}
    for row in rows:
        group = _group_of(row)
        current = best.get(group, _NONE)
        best[group] = min(current, _supplier_rank(row, rank))
    return best


def priority_first(rows: list[RowItem], priority_suppliers: tuple[str, ...]) -> list[RowItem]:
    """Группы с приоритетным поставщиком первыми; внутри группы приоритетные строки впереди, остальное как было."""
    rank = {supplier: index for index, supplier in enumerate(priority_suppliers)}
    best = _best_rank_by_group(rows, rank)

    def sort_key(row: RowItem) -> tuple[int, int, int]:
        group = _group_of(row)
        return best[group], group, _supplier_rank(row, rank)

    return sorted(rows, key=sort_key)
