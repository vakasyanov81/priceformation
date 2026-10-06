"""Стратегии слота `rest`: остаток строки для отсечки по минимуму."""

from __future__ import annotations

from domain.row_item.row_item import RowItem


class CountRest:
    """Остаток как есть (`rest_count`)."""

    def item_rest(self, row_item: RowItem) -> int | None:
        """Вернуть складской остаток."""
        return row_item.stock.rest_count


class MinusReserveRest:
    """Остаток за вычетом резерва (`rest_count - reserve_count`)."""

    def item_rest(self, row_item: RowItem) -> int | None:
        """Вернуть остаток минус резерв (Пионер)."""
        rest = row_item.stock.rest_count or 0
        reserve = row_item.stock.reserve_count or 0
        return rest - reserve
