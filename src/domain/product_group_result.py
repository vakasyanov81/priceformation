"""Однородные пакеты позиций и общий вид результата без полей конкретной модели."""

from dataclasses import dataclass
from typing import Literal, Protocol, final

from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem


class ProductPosition(Protocol):
    """Общая принадлежность позиции; характеристики остаются в модели группы."""

    @property
    def product_group(self) -> ProductGroup: ...


class ProductGroupResult[TPosition: ProductPosition](Protocol):
    """Доступ к однородным позициям без возможности заменить их другой моделью."""

    @property
    def product_group(self) -> ProductGroup: ...

    @property
    def positions(self) -> tuple[TPosition, ...]: ...

    def merge(self, other: ProductGroupResult[ProductPosition]) -> ProductGroupResult[ProductPosition]:
        """Объединить пакеты той же модели, отклонив другую группу или модель."""
        ...


@final
@dataclass(frozen=True)
class TireAndDiskResult:
    """Пакет шин и дисков: группа задана моделью, в том числе для пустого пакета.

    Состав пакета неизменяем; сами позиции сохраняют существующий изменяемый API.
    Другие группы получают собственные пакеты после определения их моделей.
    """

    positions: tuple[RowItem, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.positions, tuple):
            raise TypeError('Позиции пакета должны быть кортежем')
        if any(not isinstance(position, RowItem) for position in self.positions):
            raise TypeError('Пакет tire_and_disk принимает только RowItem')

    @property
    def product_group(self) -> Literal[ProductGroup.TIRE_AND_DISK]:
        """Идентификатор нельзя передать отдельно от модели или заменить."""
        return ProductGroup.TIRE_AND_DISK

    def merge(self, other: ProductGroupResult[ProductPosition]) -> TireAndDiskResult:
        if not isinstance(other, TireAndDiskResult):
            raise TypeError('Пакет tire_and_disk объединяется только с той же моделью')
        return TireAndDiskResult(self.positions + other.positions)
