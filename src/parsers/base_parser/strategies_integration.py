"""Интеграция стратегий в BaseParser.

Этап 2: Библиотека стратегий — демонстрация интеграции.

Стратегии резолвятся из конфига секции при инициализации парсера.
Хуки BaseParser делегируют стратегиям, если они указаны в конфиге.
"""

from __future__ import annotations

from collections.abc import Callable

from domain.row_item.row_item import RowItem
from parsers.base_parser.row_processor import apply_min_rest
from parsers.strategies.registry import make_category_strategy
from parsers.strategies.rest_registry import make_rest_strategy
from parsers.strategies.title_registry import make_title_strategy
from parsers.vendor_config.models import VendorSection
from parsers.vendor_config.slot_configs import BehaviorConfig


class StrategiesIntegration:
    """Интеграция стратегий в BaseParser.

    При создании парсера с конфигом секции, стратегии резолвятся из конфига
    и хуки BaseParser делегируют им.
    """

    def __init__(self, section: VendorSection, behavior: BehaviorConfig) -> None:
        """Запомнить секцию и behavior, создать стратегии."""
        self._section = section
        self._behavior = behavior
        self._category_strategy = make_category_strategy(section.category, 'section.category')
        self._title_strategy = make_title_strategy(
            section.title,
            'section.title',
            manufacturer_reader=lambda: None,
        )
        self._rest_strategy = make_rest_strategy(behavior, 'behavior.rest')

    def category_for(self, row_item: RowItem) -> str | None:
        """Вызвать стратегию категории."""
        return self._category_strategy.resolve(row_item)

    def get_prepared_title(self, row_item: RowItem) -> str | None:
        """Вызвать стратегию title."""
        return self._title_strategy.prepare(row_item)

    def get_item_rest(self, row_item: RowItem) -> int | None:
        """Вызвать стратегию rest."""
        return self._rest_strategy.item_rest(row_item)

    def skip_by_min_rest(self, row_item: RowItem, min_rest: int) -> None:
        """Проверить мин. остаток."""
        rest = self.get_item_rest(row_item)
        apply_min_rest(row_item, rest, min_rest)

    def process_parsed_row(self, row_item: RowItem, min_rest: int) -> None:
        """Обработать строку по pipeline из конфига."""
        step_map: dict[str, Callable[[], object]] = {
            'title': lambda: self.get_prepared_title(row_item),
            'min_rest': lambda: self.skip_by_min_rest(row_item, min_rest),
            'category': lambda: self.category_for(row_item),
        }
        for step in self._behavior.pipeline:
            step_fn = step_map.get(step)
            if step_fn is not None:
                step_fn()
