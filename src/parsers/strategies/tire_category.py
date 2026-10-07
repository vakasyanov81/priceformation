"""Стратегия категории по размеру шины (`category.strategy: tire_size_category`).

Классификация названия: камеры, диски, ободные ленты, спецшины, а среди шин —
грузовые, легкогрузовые и легковые по размеру и маркерам.
"""

from __future__ import annotations

import re

from domain.row_item.row_item import RowItem
from parsers.strategies.protocols import CategoryContext
from parsers.vendor_config.slot_configs import CategoryConfig

CAMERA = 'Автокамера'
DISK = 'Диск'
RIM_TAPE = 'Ободная лента'
SPECIAL = 'Спецшина'
TRUCK = 'Грузовая шина'
LIGHT_TRUCK = 'Легкогрузовая шина'
PASSENGER = 'Легковая шина'

_LIGHT_TRUCK_WIDTH = 245
_SPEC_WORDS = ('сельхоз', 'спец', 'клюшка', 'индустр', 'flotation')
_TRUCK_AXLE_WORDS = ('руль.ось', 'рулев', 'вед.ось', 'ведущ', 'прицепн', 'унив.ось', 'универс')
_SPEC_SIZE_PATTERNS = (
    re.compile(r'\d+lr\d+'),  # 28LR26
    re.compile(r'\b\d{1,2}[xх]\d{1,2}[.,]\d'),  # 33х12.5
    re.compile(r'\b\d{1,2}\.\d\s*[-/]\s*\d'),  # 12.5/80-18, 16.9-28
)
_TRUCK_PATTERNS = (
    re.compile(r'r\s*(?:17[.,]5|19[.,]5|22[.,]5|24[.,]5)\b'),  # R22.5
    re.compile(r'(?<![\d./])\d{1,2}(?:[.,]\d{1,2})?\s*r\s*\d{2}(?!\d)'),  # 10.00 R20
    re.compile(r'\b\d{1,2}[.,]\d{2}\s*-\s*\d{2}\b'),  # 7.50-20
    re.compile(r'\b\d{1,2}\s*pr\b'),  # 16PR
)
_LIGHT_TRUCK_SUFFIX = re.compile(r'(?:\blt\b|r\s*\d{2}\s*lt\b)')  # R16LT
_METRIC_SIZE = re.compile(r'\b(\d{3})\s*/\s*(\d{2})\s*r?\s*-?\s*(\d{2})\s*([cс])?\b')  # 205/55R16
_INCH_SIZE = re.compile(r'\b(\d{3})\s*r\s*(\d{2})\s*([cс])?\b')  # 165 R13


class TireSizeCategory:
    """Категория шины по названию строки."""

    @classmethod
    def from_config(cls, config: CategoryConfig) -> TireSizeCategory:
        """Стратегия без параметров."""
        return cls()

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str:
        """Определить категорию по названию строки."""
        return _category_by_title(row_item.identity.title)


def _category_by_title(raw_title: str | None) -> str:
    title = (raw_title or '').lower()
    return _non_tire_category(title) or _tire_category(title)


def _non_tire_category(title: str) -> str | None:
    if 'камер' in title:
        return CAMERA
    if 'диск' in title:
        return DISK
    if 'лент' in title:
        return RIM_TAPE
    return None


def _tire_category(title: str) -> str:
    if _is_special(title):
        return SPECIAL
    if _LIGHT_TRUCK_SUFFIX.search(title):
        return LIGHT_TRUCK
    if _is_truck(title):
        return TRUCK
    return _metric_or_passenger(title)


def _metric_or_passenger(title: str) -> str:
    metric = _METRIC_SIZE.search(title)
    if metric is not None:
        profile = metric.group(4)
        width = int(metric.group(1))
        return LIGHT_TRUCK if profile is not None or width >= _LIGHT_TRUCK_WIDTH else PASSENGER
    inch = _INCH_SIZE.search(title)
    if inch is not None:
        return LIGHT_TRUCK if inch.group(3) else PASSENGER
    return PASSENGER


def _is_special(title: str) -> bool:
    if any(word in title for word in _SPEC_WORDS):
        return True
    return any(pattern.search(title) for pattern in _SPEC_SIZE_PATTERNS)


def _is_truck(title: str) -> bool:
    if any(word in title for word in _TRUCK_AXLE_WORDS):
        return True
    return any(pattern.search(title) for pattern in _TRUCK_PATTERNS)
