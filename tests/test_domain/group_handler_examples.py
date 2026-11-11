"""Минимальные реализации для проверки интерфейса, не обработчики приложения."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from domain.product_group_handler import InputFields, OutputFields
from domain.product_group_result import ProductGroupResult, TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem


def _tire_fields(row: RowItem) -> OutputFields:
    """Выходные скалярные поля существующей модели."""
    return {'title': row.identity.title, 'price': row.pricing.price_opt}


class TireHandlerExample:
    """Проверка применимости интерфейса к существующей модели шин и дисков."""

    @property
    def product_group(self) -> Literal[ProductGroup.TIRE_AND_DISK]:
        return ProductGroup.TIRE_AND_DISK

    def create_position(self, fields: InputFields) -> RowItem:
        return RowItem(dict(fields))

    def process(self, positions: Sequence[RowItem]) -> TireAndDiskResult:
        return TireAndDiskResult(tuple(positions))

    def group(self, package: ProductGroupResult[RowItem]) -> TireAndDiskResult:
        return TireAndDiskResult(package.positions)

    def prepare_output(self, package: ProductGroupResult[RowItem]) -> tuple[OutputFields, ...]:
        return tuple(_tire_fields(row) for row in package.positions)


@dataclass(frozen=True)
class TestPosition:
    """Произвольная тестовая модель: не утверждает поля будущего аккумулятора."""

    __test__ = False

    label: str

    @property
    def product_group(self) -> Literal[ProductGroup.BATTERIES]:
        return ProductGroup.BATTERIES


@dataclass(frozen=True)
class TestGroupResult:
    """Вторая модель существует только в тестах интерфейса."""

    __test__ = False

    positions: tuple[TestPosition, ...]

    @property
    def product_group(self) -> Literal[ProductGroup.BATTERIES]:
        return ProductGroup.BATTERIES


class OtherHandlerExample:
    """Вторая реализация не требует шинных методов и характеристик."""

    @property
    def product_group(self) -> Literal[ProductGroup.BATTERIES]:
        return ProductGroup.BATTERIES

    def create_position(self, fields: InputFields) -> TestPosition:
        label = fields['label']
        if not isinstance(label, str):
            raise TypeError('Тестовая метка должна быть строкой')
        return TestPosition(label)

    def process(self, positions: Sequence[TestPosition]) -> TestGroupResult:
        return TestGroupResult(tuple(positions))

    def group(self, package: ProductGroupResult[TestPosition]) -> TestGroupResult:
        return TestGroupResult(package.positions)

    def prepare_output(self, package: ProductGroupResult[TestPosition]) -> tuple[OutputFields, ...]:
        return tuple({'label': position.label} for position in package.positions)
