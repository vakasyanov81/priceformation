"""Стратегии наценки: новый порог грузовых Мим."""

from __future__ import annotations

from parsers.base_parser.markup_policy import MarkupPolicy
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

    def apply(self, price_opt: float, price_recommended: float | None) -> float:
        """Отпускная до округления: процент зависит только от закупа."""
        opt = price_opt or 0
        percent = self._low if opt <= self._threshold else self._high
        return get_markup(opt, percent)
