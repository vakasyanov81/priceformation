"""Выбор главного дубля в группе: обычный товар, свежая партия, самая низкая цена."""

from domain.row_item.row_item import RowItem

# Позиция без года выпуска — считается свежей: поставщики пишут год только у старых партий.
_UNDATED = float('inf')


def _freshness(row_item: RowItem) -> float:
    return row_item.stock.production_year or _UNDATED


def main_double(row_items: list[RowItem]) -> RowItem:
    """Главный дубль группы.

    Уценка главным не становится, пока есть обычный товар; среди обычных главным
    становится самая свежая партия, внутри неё — самая низкая цена.
    """
    candidates = [row_item for row_item in row_items if not row_item.stock.marked_down] or row_items
    freshest = max(map(_freshness, candidates))
    fresh = [row_item for row_item in candidates if _freshness(row_item) == freshest]
    return min(fresh, key=lambda row_item: row_item.pricing.price_markup)
