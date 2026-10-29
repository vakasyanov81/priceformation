"""Склады Форточек: справочник API, склад для выгрузки и группа складов из настроек (чистые данные)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FourTochkiApiWarehouse:
    """Склад из справочника API (GetWarehouses): ID и название."""

    id: int
    name: str


@dataclass(frozen=True)
class FourTochkiWarehouse:
    """Склад для выгрузки: ID в API, название в прайсе и правила вывода строк."""

    id: int
    name: str
    group: str = ''
    merge_group: str | None = None
    available: str | None = None
    delivery_period: int | None = None


@dataclass(frozen=True)
class FourTochkiWarehouseGroup:
    """Группа складов из настроек: склады, в названии которых есть одно из ключевых слов.

    `merge` — склады группы сводятся в прайсе дрома в одну строку на позицию;
    `available` и `delivery_period` — наличие и срок для строк складов группы.
    """

    name: str
    keywords: tuple[str, ...]
    merge: bool = False
    available: str | None = None
    delivery_period: int | None = None

    def matches(self, warehouse_name: str) -> bool:
        """Название склада содержит одно из ключевых слов (без учёта регистра)."""
        folded = warehouse_name.casefold()
        return any(keyword.casefold() in folded for keyword in self.keywords)

    def warehouse(self, api_warehouse: FourTochkiApiWarehouse) -> FourTochkiWarehouse:
        """Склад API с правилами группы."""
        return FourTochkiWarehouse(
            id=api_warehouse.id,
            name=api_warehouse.name,
            group=self.name,
            merge_group=self.name if self.merge else None,
            available=self.available,
            delivery_period=self.delivery_period,
        )

    def describe(self) -> str:
        """Правила группы одной строкой: объединение, наличие, срок."""
        details = ['объединяются в прайсе дрома' if self.merge else 'без объединения']
        if self.available:
            details.append(self.available)
        if self.delivery_period is not None:
            details.append(f'срок {self.delivery_period} дн.')
        return ', '.join(details)
