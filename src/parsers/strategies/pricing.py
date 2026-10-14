"""Стратегии наценки: порог грузовых Мим и диапазон по категории."""

from __future__ import annotations

from parsers.base_parser.markup_policy import MarkupPolicy, RecommendedOrMapMarkupPolicy
from parsers.base_parser.price_markup import get_markup
from parsers.data_provider.models import MarkupRulesConfig


class PercentByThresholdMarkupPolicy(MarkupPolicy):
    """Наценка по порогу закупа: низкий процент до порога, высокий после (грузовые Мим)."""

    def __init__(self, threshold: float, low: float, high: float) -> None:
        """Запомнить порог и проценты по обе стороны порога."""
        super().__init__(MarkupRulesConfig(), ())
        self._threshold = threshold
        self._low = low
        self._high = high

    def apply(self, price_opt: float, price_recommended: float | None, type_production: str | None = None) -> float:
        """Отпускная до округления: процент зависит только от закупа."""
        opt = price_opt or 0
        percent = self._low if opt <= self._threshold else self._high
        return get_markup(opt, percent)


class RecommendedRangeMarkupPolicy(RecommendedOrMapMarkupPolicy):
    """РРЦ с нижней границей наценки и клампом карты по диапазону категории.

    Для категории из `rules.category_markup_ranges`:
    - РРЦ есть — цена не ниже `закуп * (1 + min)`; выше максимума РРЦ оставляем
      как у поставщика (диапазон ограничивает только снизу);
    - РРЦ нет — процент карты зажимается в `[min, max]`.
    Категории вне карты считаются как `recommended_or_map`. Затем применяется
    абсолютный пол (`absolute_markup_rules`).
    """

    def apply(self, price_opt: float, price_recommended: float | None, type_production: str | None = None) -> float:
        """Отпускная до округления с учётом диапазона категории и абсолютного пола."""
        price_range = self._rules.category_markup_ranges.get(type_production or '')
        if price_range is None:
            price = super().apply(price_opt, price_recommended)
        elif price_recommended:
            price = max(price_recommended, get_markup(price_opt, price_range.min))
        else:
            percent = min(max(self.markup_percent_for_opt(price_opt), price_range.min), price_range.max)
            price = get_markup(price_opt, percent)
        if self._is_small_absolute_markup(price, price_opt):
            price = self._price_with_absolute_rule(price_opt)
        return price
