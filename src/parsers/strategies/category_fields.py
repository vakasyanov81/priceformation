"""Поля позиции по категории, определённой по размеру названия (`category.size_fields`)."""

from __future__ import annotations

from collections.abc import Mapping

from domain.row_item.row_item import RowItem
from parsers.strategies.product_type import ProductTypeClassifier


class CategoryFields:
    """Проставить поля позиции по категории, определённой независимым классификатором.

    Категория считается `ProductTypeClassifier` — тем же расчётом, что слой
    независимого типа, — и не зависит от стратегии слота `category`. Название
    попало в категорию — незаполненные поля получают значения из конфига
    (грузовые и спецшины: ``season: Всесезонная``). Сравнение — по строке типа.
    """

    def __init__(self, mapping: Mapping[str, Mapping[str, str]]) -> None:
        """Запомнить карту «категория по размеру → поля позиции»."""
        self._mapping = mapping
        self._classifier = ProductTypeClassifier()

    def apply(self, row_item: RowItem) -> None:
        """Дописать поля по категории названия, не перетирая заполненные."""
        category = self._classifier.classify(row_item)
        fields = self._mapping.get(category)
        if not fields:
            return
        for key, field_value in fields.items():
            if not row_item.get_field(key):
                row_item.set_field(key, field_value)
