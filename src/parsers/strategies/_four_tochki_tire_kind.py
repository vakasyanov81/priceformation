"""Тип шины four_tochki: приведение типа API к типу прайса xlsx."""

from __future__ import annotations

from domain.row_item.row_item import RowItem

# Тип шины API → тип прайса xlsx (по парам позиций обоих источников): внедорожные и легкогрузовые —
# легковые, сельхоз и погрузчики — спецтехника, квадроциклы — мото.
_API_TIRE_TYPES = {
    'vned': 'легковая',
    'cartruck': 'легковая',
    'selhoz': 'спецтехника',
    'loader': 'спецтехника',
    'quadbike': 'мото',
}


def tire_kind(row_item: RowItem) -> str:
    """Тип шины в нижнем регистре, как в прайсе xlsx."""
    raw = (row_item.tire.tire_type or '').lower()
    return _API_TIRE_TYPES.get(raw, raw)


def is_truck_tire(row_item: RowItem) -> bool:
    """Грузовая шина?"""
    return tire_kind(row_item) == 'грузовая'


def is_special_tire(row_item: RowItem) -> bool:
    """Спецтехника?"""
    return tire_kind(row_item) == 'спецтехника'
