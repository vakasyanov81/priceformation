"""Протоколы стратегий: контракт слота `category`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from domain.row_item.row_item import RowItem

type BrandProbe = Callable[[str | None], bool]
"""Детектор бренда в title: True, если название содержит известный бренд."""


class CategoryContext(Protocol):
    """Сервисы парсера, нужные стратегии категории."""

    def find_canonical_category(self, raw_type: str | None) -> str | None:
        """Сопоставить категорию поставщика известному типу товара."""
        ...

    def record_unknown_category(self, raw_label: str) -> None:
        """Зафиксировать неизвестную категорию в статистике разбора."""
        ...


class CategoryStrategy(Protocol):
    """Назначение категории строки (`type_production`)."""

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
        """Вернуть категорию или None, чтобы не менять `type_production`."""
        ...


class TitleStrategy(Protocol):
    """Подготовка названия строки."""

    def prepare(self, row_item: RowItem) -> str | None:
        """Вернуть подготовленный title или None, чтобы оставить исходный."""
        ...


class RestStrategy(Protocol):
    """Остаток строки для отсечки по минимальному остатку."""

    def item_rest(self, row_item: RowItem) -> int | None:
        """Вернуть остаток по правилу слота `rest`."""
        ...
