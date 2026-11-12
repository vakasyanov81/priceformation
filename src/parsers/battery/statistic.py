"""Статистика наценки аккумуляторов по закупочной цене и фактической цене продажи."""

from collections.abc import Sequence
from decimal import Decimal

from domain.battery.item import BatteryItem

_ROUND_DIGITS = 1
_PERCENT = 100


def _range(amounts: Sequence[Decimal]) -> tuple[float, float]:
    """Округлить только итоговые границы, сохраняя точность расчёта денег."""
    if not amounts:
        return 0, 0
    lowest = round(float(min(amounts)), _ROUND_DIGITS)
    highest = round(float(max(amounts)), _ROUND_DIGITS)
    return lowest, highest


class BatteryResultStatistic:
    """Количество всех итоговых позиций и наценка предложений с известными ценами."""

    def __init__(self, positions: Sequence[BatteryItem]) -> None:
        self._count = len(positions)
        self._margins: list[Decimal] = []
        self._percents: list[Decimal] = []
        for position in positions:
            purchase = position.offer.price_opt
            sale = position.offer.sale_price
            if purchase is not None and purchase > 0 and sale is not None:
                margin = sale - purchase
                self._margins.append(margin)
                self._percents.append(margin / purchase * _PERCENT)

    def count_items(self) -> int:
        """Отсутствие закупочной цены не уменьшает число обработанных товаров."""
        return self._count

    def real_percents_markup(self) -> tuple[float, float]:
        """Наценка относительно закупочной цены; нули при отсутствии ценовых пар."""
        return _range(self._percents)

    def real_absolute_markup(self) -> tuple[float, float]:
        """Разница между ценой продажи и закупочной ценой в рублях."""
        return _range(self._margins)
