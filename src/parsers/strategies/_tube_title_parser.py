"""Разбор названия камеры и ободной ленты Пошка, STK и Пионера: размер.

Форматы названия (после префикса ``Камера``/``Автокамера``/``Ободная лента`` и необязательных слов без цифр, ``СВК``):

- ``Камера СВК 20.5-25 ГК-260 (0)`` — ширина и посадочный диаметр;
- ``Автокамера 12.5/80-18``, ``Ободная лента 16/70-20 (300-508)`` — с профилем;
- ``Камера СВК 1200х500-508 РК-5А-145 (65)``, ``Камера 1200-500-508 ОШЗ`` — внешний диаметр, ширина, посадочный;
- ``Камера СВК 15.5-18/16.5-18 ГК-115 (60)`` — второй размер остаётся в названии, берётся первый.

Бренд и модель не разбираются: ``СВК``/``ГК-145``/``ТК`` — тип камеры, бренд — отдельная задача.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from domain.row_item.row_item import RowItem
from parsers.strategies._tire_title_parser import TUBE_PREFIX, parse_leading_size

# До размера допустимы слова без цифр: `СВК` или вставленный производитель раздела (`камера Triangle 11.2-20`).
_LEADING_WORDS = re.compile(r'^(?:[^\d\s]+\s+){0,2}')
# Лента без префикса: размер и `об/лента` в хвосте (`205-457 (12.00-18) об/лента`).
_TRAILING_TAPE = re.compile(r'\s+(?:\([^)]*\)\s*)?об/лента\s*$', re.IGNORECASE)
_SIZE_SEPARATOR = re.compile(r'(?<=\d)\s*[хХ*]\s*(?=\d)')
# `1200-500-508` — тот же дюймовый размер, где вместо `x` стоит дефис.
_THREE_DASH = re.compile(r'^(\d+)-(\d+)-(\d+)')
# Профиль шины не больше 100%: `175/185-16` — диапазон ширин, не профиль.
_MAX_PROFILE = 100


@dataclass(frozen=True, slots=True)
class TubeTitleParts:
    """Разобранный размер камеры/ленты; пустая строка — параметра нет."""

    width: str
    height_percent: str
    diameter: str
    ext_diameter: str


def parse_tube_title(raw: str | None) -> TubeTitleParts | None:
    """Разобрать название камеры/ободной ленты; None, если это не они или размер не читается."""
    if not raw:
        return None
    body = _tube_body(raw)
    if body is None:
        return None
    text = _SIZE_SEPARATOR.sub('x', body)
    text = _THREE_DASH.sub(r'\1x\2-\3', _LEADING_WORDS.sub('', text))
    size = parse_leading_size(text)
    if size is None:
        return None
    height = size.height_percent if _is_profile(size.height_percent) else ''
    return TubeTitleParts(size.width, height, size.diameter, size.ext_diameter)


def _tube_body(raw: str) -> str | None:
    """Часть названия с размером: после префикса ``Камера``/``Лента`` или перед хвостом ``об/лента``."""
    prefix = TUBE_PREFIX.match(raw)
    if prefix is not None:
        return raw[prefix.end() :].lstrip()
    tape = _TRAILING_TAPE.search(raw)
    if tape is None:
        return None
    return raw[: tape.start()]


def fill_tube_fields(row_item: RowItem, parts: TubeTitleParts) -> None:
    """Записать размер в поля позиции, не перетирая готовые."""
    fields = {
        'width': parts.width,
        'height_percent': parts.height_percent,
        'diameter': parts.diameter,
        'ext_diameter': parts.ext_diameter,
    }
    for key, parsed_value in fields.items():
        if parsed_value and not row_item.get_field(key):
            row_item.set_field(key, parsed_value)


def _is_profile(percent: str) -> bool:
    """Значение — профиль в процентах, а не вторая ширина."""
    return bool(percent) and float(percent) <= _MAX_PROFILE
