"""Value Object: цены и наценки."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Pricing:
    """Ценовые поля позиции."""

    price_opt: float = 0
    price_recommended: float = 0
    price_markup: float = 0
    percent_markup: float = 0

    @classmethod
    def from_flat(cls, store: dict[str, Any]) -> Pricing:
        """Собрать из плоского словаря."""
        return cls(
            price_opt=store.get('price_opt', 0),
            price_recommended=store.get('price_recommended', 0),
            price_markup=store.get('price_markup', 0),
            percent_markup=store.get('percent_markup', 0),
        )

    def to_flat(self) -> dict[str, Any]:
        """В плоский словарь."""
        return {
            'price_opt': self.price_opt,
            'price_recommended': self.price_recommended,
            'price_markup': self.price_markup,
            'percent_markup': self.percent_markup,
        }
