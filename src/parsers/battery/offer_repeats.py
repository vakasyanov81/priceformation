"""Повторы адреса предложения поставщика не создают дополнительный остаток."""

from dataclasses import replace

from domain.battery.duplicate import BatteryDuplicate
from domain.battery.item import BatteryItem


def unique_offers(positions: tuple[BatteryItem, ...]) -> list[BatteryItem]:
    """Отделить удаление точных повторов от сравнения товаров по параметрам."""
    seen: dict[tuple[str, str], BatteryItem] = {}
    kept: list[BatteryItem] = []
    for original in positions:
        position = replace(original, duplicate=BatteryDuplicate())
        if is_new_offer(position, seen):
            kept.append(position)
    return kept


def is_new_offer(position: BatteryItem, seen: dict[tuple[str, str], BatteryItem]) -> bool:
    """Конфликт требует исправления входа; неизвестный адрес не удаляет строку."""
    supplier, code = position.offer.supplier_name, position.identity.code
    if supplier is None or code is None:
        return True
    address = (supplier, code)
    if address not in seen:
        seen[address] = position
        return True
    if seen[address] != position:
        raise ValueError(f'[batteries] {supplier}, код {code}: конфликт повторных предложений')
    return False
