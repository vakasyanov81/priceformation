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


# Дубль, чья цена отличается от цены главного дубля на эту долю и больше, считается сомнительным.
_DOUBTFUL_PRICE_DEVIATION = 0.05


def is_doubtful_price(row_item: RowItem, main_item: RowItem) -> bool:
    """Закупочная цена дубля отклоняется от закупочной цены главного дубля на 5% и более (в любую сторону)."""
    main_price = main_item.pricing.price_opt
    if not main_price:
        return False
    return abs(row_item.pricing.price_opt - main_price) / main_price >= _DOUBTFUL_PRICE_DEVIATION
