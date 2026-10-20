"""Название камеры и ободной ленты из текста поставщика: размер, бренд, модель."""

from __future__ import annotations

import re

from domain.row_item.row_item import RowItem
from parsers.common_price_title_flags import has_valve, tube_model_from_title
from parsers.nomenclature_brand import brand_label
from parsers.nomenclature_tube_title import compose_tube_title, tube_size_label
from parsers.strategies._tire_title_parser import TUBE_PREFIX
from parsers.strategies._tube_title_parser import parse_tube_title
from parsers.strategies.protocols import ManufacturerProbe

_RIM_TAPE_WORD = re.compile(r'лент', re.IGNORECASE)


def compose_tube_title_from_text(
    row_item: RowItem,
    title: str | None,
    manufacturer_probe: ManufacturerProbe | None = None,
) -> str | None:
    """Каноническое название камеры или ободной ленты; None, если это не они или в тексте нет размера.

    Камера или лента без размера (``Камера УК-14-02 ОШЗ``) остаётся текстом поставщика и помечается
    ``title_not_composed`` для статистики разбора.

    Размер и модель (``ГК-145``, ``УК-13М``, ``300-508А``) разбираются из текста поставщика. Бренд ищет
    ``manufacturer_probe`` в тексте (поле позиции на этом шаге ещё пусто: производитель определяется по названию),
    иначе берётся поле.
    Слова ``СВК``, ``(25)``, ``Китай`` в название не входят. Модель остаётся: она режет группу дублей
    (``common_price_title_flags.tube_model``).
    """
    parts = parse_tube_title(title)
    if parts is None:
        if TUBE_PREFIX.match(title or ''):
            row_item.set_field('title_not_composed', True)
        return None
    size = tube_size_label(parts.width, parts.height_percent, parts.diameter, parts.ext_diameter, parts.width_max)
    is_rim_tape = bool(_RIM_TAPE_WORD.search(title or ''))
    model = tube_model_from_title(title, is_rim_tape=is_rim_tape)
    brand = _brand(row_item, title, manufacturer_probe)
    return compose_tube_title(is_rim_tape, size, brand, model, valve=has_valve(title))


def _brand(row_item: RowItem, title: str | None, manufacturer_probe: ManufacturerProbe | None) -> str:
    """Производитель из текста поставщика, иначе из поля позиции."""
    found = manufacturer_probe(title) if manufacturer_probe else None
    return found or brand_label(row_item)
