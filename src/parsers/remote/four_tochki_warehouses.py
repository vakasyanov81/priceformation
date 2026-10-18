"""Склады Форточек для выгрузки по API: группы складов по ключевым словам из настроек."""

import json
from dataclasses import dataclass
from typing import Any

from domain.config_context import get_config_provider
from domain.exceptions import ConfigValidationError
from infrastructure.data.file_reader import read_file
from parsers.data_provider.json_fields import read_flag
from parsers.vendor_config.fields import read_int, read_str_list, read_text

WAREHOUSES_CONFIG_FILE = 'four_tochki_warehouses.json'


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


def load_four_tochki_warehouse_groups() -> tuple[FourTochkiWarehouseGroup, ...]:
    """Группы складов из parse_config/four_tochki_warehouses.json."""
    raw = read_file(get_config_provider().config_file(WAREHOUSES_CONFIG_FILE))
    return parse_warehouse_groups(json.loads(raw))


def parse_warehouse_groups(payload: Any) -> tuple[FourTochkiWarehouseGroup, ...]:
    """Проверить структуру файла и собрать группы; ошибка — с путём до ключа."""
    entries = payload.get('groups') if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        raise ConfigValidationError(
            f'{WAREHOUSES_CONFIG_FILE}: ожидается объект с ключом «groups» — списком групп складов',
        )
    if not entries:
        raise ConfigValidationError(f'{WAREHOUSES_CONFIG_FILE} → groups: список групп пуст')
    groups = []
    for index, entry in enumerate(entries):
        where = f'{WAREHOUSES_CONFIG_FILE} → groups[{index}]'
        groups.append(_group(entry, where))
    _ensure_unique_names(groups)
    return tuple(groups)


def _group(entry: Any, where: str) -> FourTochkiWarehouseGroup:
    if not isinstance(entry, dict):
        raise ConfigValidationError(f'{where}: ожидается объект группы, получено {entry!r}')
    keywords = tuple(keyword.strip() for keyword in read_str_list(entry, 'keywords', where))
    if not keywords or not all(keywords):
        raise ConfigValidationError(f'{where} → keywords: ожидается непустой список непустых строк')
    delivery_period = read_int(entry, 'delivery_period', where) if 'delivery_period' in entry else None
    return FourTochkiWarehouseGroup(
        name=read_text(entry, 'name', where),
        keywords=keywords,
        merge=read_flag(entry, 'merge', where),
        available=read_text(entry, 'available', where, default='') or None,
        delivery_period=delivery_period,
    )


def _ensure_unique_names(groups: list[FourTochkiWarehouseGroup]) -> None:
    seen: set[str] = set()
    for group in groups:
        if group.name in seen:
            raise ConfigValidationError(f'{WAREHOUSES_CONFIG_FILE}: группа «{group.name}» указана дважды')
        seen.add(group.name)
