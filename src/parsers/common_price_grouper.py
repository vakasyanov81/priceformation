"""Группировка строк прайса по параметрам наименования."""

from itertools import groupby
from typing import Any, List, Optional, Tuple

from parsers.row_item.row_item import RowItem


def sanitize_value(price_list_values: List[Any]) -> Tuple[str, ...]:
    """Преобразует значения в строки, корректно обрабатывая None."""
    return tuple("" if price_list_val is None else str(price_list_val) for price_list_val in price_list_values)


class CommonPriceGrouper:
    """Группировка результата разбора прайсов поставщиков по параметрам наименований"""

    def __init__(self, row_items: List[RowItem]):
        self.row_items = row_items
        self._is_grouped = False

    def group_by_params(self) -> "CommonPriceGrouper":
        """Группировка списка по параметрам и разметка дублей."""
        if self._is_grouped:
            return self

        self._assign_orders()
        self._assign_groups()
        self.row_items.sort(key=lambda grouped: (grouped.group_by_params, grouped.order))
        self._is_grouped = True
        return self

    def _assign_orders(self) -> None:
        """Проставить исходный порядок (O(N))."""
        for idx, row_item in enumerate(self.row_items, start=1):
            row_item.order = idx

    def _assign_groups(self) -> None:
        """Сгруппировать, разметить дубли и выставить group_by_params."""
        group_id = 0
        sorted_items = sorted(self.row_items, key=self.group_key)
        for _key, group_iter in groupby(sorted_items, key=self.group_key):
            group_id += 1
            self._apply_group(group_id, list(group_iter))

    def _apply_group(self, group_id: int, group_items: List[RowItem]) -> None:
        """Обработать одну группу дублей."""
        self._mark_double_items(group_items)
        for row_item in group_items:
            row_item.group_by_params = group_id

    def get_row_items(self) -> List[RowItem]:
        """Получить сгруппированные позиции."""
        if not self._is_grouped:
            self.group_by_params()
        return self.row_items

    @classmethod
    def _mark_double_items(cls, row_items: List[RowItem]) -> None:
        """Проставить признаки дублей внутри одной группы."""
        if len(row_items) < 2:
            return

        min_price_item = min(row_items, key=lambda row_item: row_item.price_markup)

        for row_item in row_items:
            if row_item.order == min_price_item.order:
                row_item.double_candidate = True
            else:
                row_item.is_double = True

    def get_double_count(self) -> int:
        """Получить количество дублей."""
        return len(self.get_double_row_items())

    def get_double_row_items(self) -> List[RowItem]:
        """Получить список дублей."""
        if not self._is_grouped:
            self.group_by_params()
        return [
            row_item
            for row_item in self.row_items
            if getattr(row_item, "is_double", False) or getattr(row_item, "double_candidate", False)
        ]

    @classmethod
    def group_key(cls, row_item: RowItem) -> Tuple[str, ...]:
        """Ключ группировки."""
        return sanitize_value(cls._group_key_parts(row_item))

    @classmethod
    def _group_key_parts(cls, row_item: RowItem) -> List[Any]:
        """Значения полей для ключа группировки."""
        mark = (row_item.manufacturer or "").lower()
        brand = (row_item.brand or "").lower()
        brand = "" if brand == mark else brand
        return [
            (row_item.type_production or "").lower(),
            row_item.width,
            row_item.diameter,
            row_item.height_percent,
            row_item.index_velocity,
            row_item.index_load,
            cls.clear_model(row_item.model),
            mark,
            row_item.axis,
            row_item.layering,
            row_item.slot_count,
            row_item.central_diameter,
            row_item.slot_diameter,
            row_item.color,
            brand,
            row_item.eet,
            row_item.intimacy or cls.define_intimacy(row_item),
        ]

    @classmethod
    def define_intimacy(cls, row_item: RowItem) -> Optional[str]:
        """Определить камерность (TL/TT/TTF) из title."""
        found = cls._intimacy_from_title(row_item.title)
        if found:
            return found
        return cls._default_truck_intimacy(row_item)

    @classmethod
    def _intimacy_from_title(cls, title: Optional[str]) -> Optional[str]:
        """Искать TL/TT/TTF в словах title."""
        chunks = (title or "").lower().split()
        for intimacy in ("tl", "tt", "ttf"):
            if intimacy in chunks:
                return intimacy.upper()
        return None

    @classmethod
    def _default_truck_intimacy(cls, row_item: RowItem) -> Optional[str]:
        """TL для грузовых с дробным диаметром."""
        type_prod = (row_item.type_production or "").lower()
        if "грузовая" in type_prod and cls._is_float_diameter(row_item.diameter):
            return "TL"
        return None

    @classmethod
    def _is_float_diameter(cls, diameter: Any) -> bool:
        """Диаметр не целое число (например 15.3)."""
        diameter_str = str(diameter or 0).replace(",", ".")
        try:
            return not float(diameter_str).is_integer()
        except (ValueError, TypeError):
            return False

    @classmethod
    def clear_model(cls, model: Optional[str]) -> str:
        """Очистка названия модели от пробелов и префиксов до дефиса."""
        if not model:
            return ""

        model = model.replace(" ", "")
        parts = model.split("-")

        # Если есть дефис, берем вторую часть, иначе всю строку
        return parts[1] if len(parts) > 1 else parts[0]
