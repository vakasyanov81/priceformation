"""Склады Форточек для выгрузки по API: группы складов по ключевым словам из настроек."""

import json
from typing import Any

from domain.config_context import get_config_provider
from domain.exceptions import ConfigValidationError
from domain.four_tochki import FourTochkiWarehouseGroup
from infrastructure.data.file_reader import read_file
from parsers.data_provider.json_fields import read_flag
from parsers.vendor_config.fields import read_int, read_str_list, read_text

WAREHOUSES_CONFIG_FILE = 'four_tochki_warehouses.json'


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
