from itertools import groupby
from typing import List, Optional, Tuple, Any

from parsers.row_item.row_item import RowItem


def sanitize_value(values: List[Any]) -> Tuple[str, ...]:
    """Преобразует значения в строки, корректно обрабатывая None."""
    return tuple(str(val) if val is not None else "" for val in values)


class CommonPriceGrouper:
    """Группировка результата разбора прайсов поставщиков по параметрам наименований"""

    def __init__(self, items: List[RowItem]):
        self.items = items
        self._is_grouped = False

    def group_by_params(self) -> "CommonPriceGrouper":
        """Группировка списка по параметрам и разметка дублей."""
        if self._is_grouped:
            return self

        # 1. Проставляем исходный порядок (O(N))
        for idx, item in enumerate(self.items, start=1):
            item.order = idx

        # 2. Сортируем по ключу группировки (необходимо для itertools.groupby)
        sorted_items = sorted(self.items, key=self.group_key)

        group_id = 0
        for key, group_iter in groupby(sorted_items, key=self.group_key):
            group_id += 1
            group_items = list(group_iter)

            # Обрабатываем дубли внутри текущей группы
            self._mark_double_items(group_items)

            # Присваиваем ID группы всем элементам этой группы
            for item in group_items:
                item.group_by_params = group_id

        # 3. Сортируем итоговый список: сначала по группе, потом по исходному порядку.
        # Это лучше, чем просто восстанавливать исходный порядок, так как дубли остаются рядом.
        self.items.sort(key=lambda x: (x.group_by_params, x.order))

        self._is_grouped = True
        return self

    def get_items(self) -> List[RowItem]:
        if not self._is_grouped:
            self.group_by_params()
        return self.items

    @classmethod
    def _mark_double_items(cls, items: List[RowItem]) -> None:
        """Проставить признаки дублей внутри одной группы."""
        if len(items) < 2:
            return

        min_price_item = min(items, key=lambda x: x.price_markup)

        for item in items:
            if item.order == min_price_item.order:
                item.double_candidate = True
            else:
                item.is_double = True

    def get_double_count(self) -> int:
        """Получить количество дублей."""
        return len(self.get_double_items())

    def get_double_items(self) -> List[RowItem]:
        """Получить список дублей."""
        if not self._is_grouped:
            self.group_by_params()
        return [
            item for item in self.items if getattr(item, 'is_double', False) or getattr(item, 'double_candidate', False)
        ]

    @classmethod
    def group_key(cls, item: RowItem) -> Tuple[str, ...]:
        """Ключ группировки."""
        width = item.width
        diameter = item.diameter
        profile = item.height_percent
        velocity = item.index_velocity
        load = item.index_load
        model = cls.clear_model(item.model)
        mark = (item.manufacturer or "").lower()

        axis = item.axis
        layering = item.layering
        intimacy = item.intimacy or cls.define_intimacy(item)

        slot_count = item.slot_count
        dia = item.central_diameter
        slot_diameter = item.slot_diameter
        color = item.color
        _et = item.eet

        brand = (item.brand or "").lower()
        if brand == mark:
            brand = ""

        type_prod = (item.type_production or "").lower()

        return sanitize_value(
            [
                type_prod,
                width,
                diameter,
                profile,
                velocity,
                load,
                model,
                mark,
                axis,
                layering,
                slot_count,
                dia,
                slot_diameter,
                color,
                brand,
                _et,
                intimacy,
            ]
        )

    @classmethod
    def define_intimacy(cls, item: RowItem) -> Optional[str]:
        l_title = (item.title or "").lower()
        diameter_str = str(item.diameter or 0).replace(",", ".")

        is_float_diameter = False
        try:
            is_float_diameter = not float(diameter_str).is_integer()
        except (ValueError, TypeError):
            pass  # Если не удалось преобразовать, считаем, что не float

        # split() без аргументов автоматически обрабатывает множественные пробелы
        title_chunks = l_title.split()

        for intimacy_ in ("tl", "tt", "ttf"):
            if intimacy_ in title_chunks:
                return intimacy_.upper()

        type_prod = (item.type_production or "").lower()
        if "грузовая" in type_prod and is_float_diameter:
            return "TL"

        return None

    @classmethod
    def clear_model(cls, model: Optional[str]) -> str:
        """Очистка названия модели от пробелов и префиксов до дефиса."""
        if not model:
            return ""

        model = model.replace(" ", "")
        parts = model.split("-")

        # Если есть дефис, берем вторую часть, иначе всю строку
        return parts[1] if len(parts) > 1 else parts[0]
