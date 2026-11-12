"""Однородный пакет аккумуляторных позиций."""

from dataclasses import dataclass
from typing import Literal, final

from domain.battery.item import BatteryItem
from domain.product_group_result import ProductGroupResult, ProductPosition
from domain.product_groups import ProductGroup


@final
@dataclass(frozen=True)
class BatteryResult:
    """Состав неизменяем; чужая модель отклоняется, в том числе на границе Python."""

    positions: tuple[BatteryItem, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.positions, tuple):
            raise TypeError('Позиции пакета должны быть кортежем')
        if any(not isinstance(position, BatteryItem) for position in self.positions):
            raise TypeError('Пакет batteries принимает только BatteryItem')

    @property
    def product_group(self) -> Literal[ProductGroup.BATTERIES]:
        """Пустой результат также сохраняет свою группу."""
        return ProductGroup.BATTERIES

    def merge(self, other: ProductGroupResult[ProductPosition]) -> BatteryResult:
        """Объединить только аккумуляторы с сохранением порядка и исходных пакетов."""
        if not isinstance(other, BatteryResult):
            raise TypeError('Пакет batteries объединяется только с той же моделью')
        return BatteryResult(self.positions + other.positions)
