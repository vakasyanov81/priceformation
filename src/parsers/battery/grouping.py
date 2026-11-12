"""Группировка аккумуляторов с независимыми остатками предложений."""

from dataclasses import replace
from decimal import Decimal

from domain.battery.duplicate import BatteryDuplicate
from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from parsers.battery.group_keys import identity_key, known_parts, optional_key, resolve_optional
from parsers.battery.offer_repeats import unique_offers


def split_optional(positions: list[BatteryItem]) -> list[list[BatteryItem]]:
    """Неизвестное совместимо только с единственным вариантом всего основного ключа."""
    keys = [optional_key(position) for position in positions]
    variants = list(map(known_parts, zip(*keys, strict=True)))
    groups: dict[tuple[object, ...], list[BatteryItem]] = {}
    for position, key in zip(positions, keys, strict=True):
        groups.setdefault(resolve_optional(key, variants), []).append(position)
    return list(groups.values())


def offer_price(position: BatteryItem) -> Decimal:
    """Неизвестная РРЦ не выигрывает у известной; ноль является известной ценой."""
    price = position.offer.sale_price
    return Decimal('Infinity') if price is None else price


def main_groups(package: BatteryResult) -> list[list[BatteryItem]]:
    """Неполный основной ключ создаёт отдельную группу для каждого предложения."""
    buckets: dict[tuple[object, ...], list[BatteryItem]] = {}
    for index, position in enumerate(unique_offers(package.positions)):
        key = identity_key(position)
        if None in key:
            key = (index,)
        buckets.setdefault(key, []).append(position)
    return list(buckets.values())


def mark_group(group_id: int, positions: list[BatteryItem]) -> list[BatteryItem]:
    """Минимальная цена и исходный порядок определяют главное предложение."""
    main = min(positions, key=offer_price)
    return [replace(position, duplicate=BatteryDuplicate(group_id, position is main)) for position in positions]


def group_batteries(package: BatteryResult) -> BatteryResult:
    """Разметить дубли без потери цен, характеристик и отдельных остатков."""
    groups = [group for bucket in main_groups(package) for group in split_optional(bucket)]
    marked: list[BatteryItem] = []
    for group_id, positions in enumerate(groups, start=1):
        marked.extend(mark_group(group_id, positions))
    return BatteryResult(tuple(marked))
