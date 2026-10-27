"""Категория позиции: стратегия категории, независимый тип товара, поля по размеру."""

import logging

from domain.row_item.row_item import RowItem
from parsers.base_parser.category_finder import CategoryFinder
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.row_processor import correction_category
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.strategies.product_types import declared_matches

logger = logging.getLogger(__name__)


class CategoryLookup:
    """Справочник категорий и статистика разбора: контекст (`CategoryContext`) для стратегии категории."""

    def __init__(self, stats: ParserStats) -> None:
        self._stats = stats
        self._finder: CategoryFinder | None = None

    def reset(self) -> None:
        """Начать разбор заново: новый `CategoryFinder`."""
        self._finder = CategoryFinder()

    def find_canonical_category(self, raw_type: str | None) -> str | None:
        """Сопоставить категорию поставщика известному типу (CategoryContext)."""
        if self._finder is None:
            self._finder = CategoryFinder()
        return self._finder.find_canonical(raw_type)

    def record_unknown_category(self, raw_label: str) -> None:
        """Зафиксировать неизвестную категорию в статистике разбора (CategoryContext)."""
        self._stats.unknown_category_skips.append(raw_label)

    def correction_category(self, row_item: RowItem) -> None:
        correction_category(row_item, self._finder)


class CategoryService:
    """Определение категории и типа товара по стратегиям из хуков."""

    def __init__(self, hooks: StrategyHooks | None, lookup: CategoryLookup) -> None:
        self._hooks = hooks
        self.lookup = lookup

    def category_for(self, row_item: RowItem) -> str | None:
        """Категория строки. Стратегия или None. Контекст — справочник категорий."""
        if self._hooks and self._hooks.category is not None:
            return self._hooks.category.resolve(row_item, self.lookup)
        return None

    def apply_category(self, row_item: RowItem) -> None:
        """Назначить `type_production`: независимый тип или заявленный стратегией.

        При включённом `product_type` в `type_production` идёт вычисленный тип,
        а `type_corrected` помечает расхождение с заявленным (конкретным) типом.
        Если свой тип не определён (`''`), остаётся заявленный — позицию без
        независимого ответа не оставляем без типа и не помечаем расхождением
        (README §7 п.4: нераспознанный тип — не повод потерять категорию).
        """
        declared = self.category_for(row_item)
        if self._hooks is not None and self._hooks.product_type is not None:
            own = self._hooks.product_type.classify(row_item)
            chosen = own or declared
            if chosen is not None:
                row_item.set_field('type_production', chosen)
            corrected = bool(own) and not declared_matches(declared, own)
            row_item.set_field('type_corrected', corrected)
            if corrected:
                title = row_item.identity.title
                logger.debug(f'Тип товара изменён: заявлено «{declared}», вычислено «{own}» // {title}')
        elif declared is not None:
            row_item.set_field('type_production', declared)

    def zero_rest_without_category(self, row_item: RowItem) -> None:
        """Обнулить остаток строки без категории, чтобы она не попала в прайс."""
        if self._hooks is not None and self._hooks.zero_rest_without_category and not row_item.vendor.type_production:
            row_item.set_field('rest_count', 0)

    def apply_category_fields(self, row_item: RowItem) -> None:
        """Дописать поля по категории-размеру названия (`category.size_fields`)."""
        if self._hooks is not None and self._hooks.category_fields is not None:
            self._hooks.category_fields.apply(row_item)
