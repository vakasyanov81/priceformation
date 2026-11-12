"""Отбор предложений аккумуляторов из групп с дублями."""

from collections import Counter

from domain.battery.item import BatteryItem


def double_positions(positions: tuple[BatteryItem, ...]) -> tuple[BatteryItem, ...]:
    """Сохранить все предложения повторяющихся групп, начиная с главного."""
    counts = Counter(position.duplicate.group_id for position in positions)
    doubles = [
        position
        for position in positions
        if position.duplicate.group_id > 0 and counts[position.duplicate.group_id] > 1
    ]
    return tuple(sorted(doubles, key=_order))


def _order(position: BatteryItem) -> tuple[int, bool]:
    return position.duplicate.group_id, not position.duplicate.is_main
