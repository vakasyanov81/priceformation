"""Поля позиции по итоговому типу и размеру шины."""

from __future__ import annotations

from collections.abc import Mapping

from domain.row_item.row_item import RowItem
from parsers.strategies.product_type import ProductTypeClassifier


class CategoryFields:
    """Применить обязательные поля по итоговому типу, затем заполнить пропуски по размеру.

    Категория считается `ProductTypeClassifier` — тем же расчётом, что слой
    независимого типа, — и не зависит от стратегии слота `category`. Название
    попало в категорию — незаполненные поля получают значения из конфига
    (грузовые и спецшины: ``season: Всесезонная``). Сравнение — по строке типа.
    """

    def __init__(
        self,
        mapping: Mapping[str, Mapping[str, str]],
        type_fields: Mapping[str, Mapping[str, str]] | None = None,
    ) -> None:
        """Запомнить карты полей по размеру и по итоговому типу."""
        self._mapping = mapping
        self._type_fields = type_fields or {}
        self._classifier = ProductTypeClassifier()

    def apply(self, row_item: RowItem) -> None:
        """Применить значения по итоговому типу и дополнить поля по размеру."""
        fields = self._type_fields.get(row_item.vendor.type_production or '', {})
        for key, field_value in fields.items():
            row_item.set_field(key, field_value)
        self._apply_size_fields(row_item)

    def _apply_size_fields(self, row_item: RowItem) -> None:
        if not self._mapping:
            return
        category = self._classifier.classify(row_item)
        fields = self._mapping.get(category)
        if not fields:
            return
        for key, field_value in fields.items():
            if not row_item.get_field(key):
                row_item.set_field(key, field_value)
