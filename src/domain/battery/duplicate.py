"""Результат группировки аккумулятора без изменения предложения поставщика."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BatteryDuplicate:
    """Локальный номер группы batteries и признак главного предложения."""

    group_id: int = 0
    is_main: bool = False
