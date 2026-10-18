"""Разбор названия диска Пошка и STK: размер, крепёж, ET, DIA, толщина, цвет, тип.

Форматы названия:

- Пошк: ``Диск штамп SRW 11.75x22.5 10x335 ET135 d281 М22 Silver (13мм) 4500 кг``;
- STK: ``Диск стальной Yongzheng 22.5x11.75 10 26мм ЕТ0 D281 раст.335 (16мм)`` —
  размер записан «диаметр x ширина», отверстий 10, ``26мм`` — диаметр отверстия, PCD — после ``раст.``;
- без PCD: ``Диск штамп Forza F-14 9x22.5 10 отв. ET175 d222``;
- только размер: ``Диск штамп 5x10 (две половинки)``.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from domain.row_item.row_item import RowItem
from parsers.strategies._title_wins import DISK_TITLE_WINS

_LEADING_DISK = re.compile(r'^\s*Диск\b\s*', re.IGNORECASE)
_DISK_TYPES = {'штамп': 'штамп', 'стальной': 'стальной'}
_SEPARATOR = re.compile(r'(?<=\d)\s*[хХ*]\s*(?=\d)')
_DECIMAL_COMMA = re.compile(r'(?<=\d),(?=\d)')
_NUMBER = r'\d+(?:\.\d+)?'
_PAIR = re.compile(rf'(?<![\w.])({_NUMBER})x({_NUMBER})(?![\w.])')
_ET = re.compile(rf'(?<!\w)[EЕ][TТ]\s*(-?{_NUMBER})', re.IGNORECASE)
_CENTRAL = re.compile(rf'(?<!\w)[dDдД]\s?({_NUMBER})(?![\w.])')
_HOLES_HOLE_SIZE = re.compile(r'(?<![\w.])(\d{1,2})\s+\d+\s*мм(?!\w)')
_HOLES_WORD = re.compile(r'(?<![\w.])(\d{1,2})\s*отв')
_PCD_WORD = re.compile(rf'раст\.?\s*({_NUMBER})', re.IGNORECASE)
_THICKNESS_PAREN = re.compile(rf'\(({_NUMBER})\s*мм\)', re.IGNORECASE)
_THICKNESS_BARE = re.compile(rf'(?<![\w.])({_NUMBER})\s*мм(?!\w)', re.IGNORECASE)
_COLORS = {
    'silver': 'Silver',
    'sil': 'Silver',
    'серебристый': 'серебристый',
    'металлик': 'металлик',
    'грунт': 'грунт',
}
_MAX_SIZE_NUMBER = 30
_MIN_PCD = 50
_SLOTS = {'3', '4', '5', '6', '7', '8', '9', '10', '11', '12'}


@dataclass(frozen=True, slots=True)
class DiskTitleParts:
    """Разобранные параметры названия диска; пустая строка — параметра нет."""

    width: str = ''
    diameter: str = ''
    slot_count: str = ''
    pcd: str = ''
    et: str = ''
    central_diameter: str = ''
    thickness: str = ''
    color: str = ''
    disk_type: str = ''

    @classmethod
    def from_text(cls, text: str, size: tuple[str, str]) -> DiskTitleParts:
        """Собрать параметры из нормализованного названия и пары размера (ширина, диаметр — по величине)."""
        width, diameter = sorted(size, key=float)
        slots, pcd = _fasteners(text)
        return cls(
            width=width,
            diameter=diameter,
            slot_count=slots,
            pcd=pcd,
            et=_first_group(_ET, text),
            central_diameter=_first_group(_CENTRAL, text),
            thickness=_thickness(text),
            color=_first_known(text, _COLORS),
            disk_type=_first_known(text, _DISK_TYPES),
        )

    @classmethod
    def first_size(cls, text: str) -> DiskTitleParts | None:
        """Параметры по первой паре размеров, похожей на размер диска."""
        for pair in _PAIR.finditer(text):
            if max(map(float, pair.groups())) <= _MAX_SIZE_NUMBER:
                return cls.from_text(text, (pair[1], pair[2]))
        return None

    @property
    def has_fasteners(self) -> bool:
        """Есть крепёж «отверстия x PCD»."""
        return bool(self.slot_count and self.pcd)

    @classmethod
    def et_from_name(cls, raw: str | None) -> str | None:
        """Вылет ET из названия диска без префикса «Диск» (Запаска, Форточки); None, если это не диск.

        Диском считаем название, где есть и ET, и крепёж «отверстия x PCD» (`4*100`): иначе
        `ET-500` из названия шины приняли бы за вылет.
        """
        if not raw:
            return None
        text = _DECIMAL_COMMA.sub('.', _SEPARATOR.sub('x', raw))
        slots, pcd = _fasteners(text)
        return _first_group(_ET, text) or None if slots and pcd else None


def parse_disk_title(raw: str | None, *, bare: bool = False) -> DiskTitleParts | None:
    """Разобрать название диска; None, если это не диск с размером.

    ``bare`` — название без слова «Диск» (API Форточек: ``7x17/5x108 ET50 D63,35 ...``);
    такое название считаем диском только при крепеже «отверстия x PCD».
    """
    if not raw or (not bare and _LEADING_DISK.match(raw) is None):
        return None
    parts = DiskTitleParts.first_size(_DECIMAL_COMMA.sub('.', _SEPARATOR.sub('x', raw)))
    return parts if parts is not None and (not bare or parts.has_fasteners) else None


def fill_disk_fields(row_item: RowItem, parts: DiskTitleParts) -> None:
    """Записать разобранные параметры в поля позиции, не перетирая готовые."""
    fields = {
        'width': parts.width,
        'diameter': parts.diameter,
        'slot_count': parts.slot_count,
        'pcd1': parts.pcd,
        'eet': parts.et,
        'central_diameter': parts.central_diameter,
        'disk_thickness': parts.thickness,
        'color': parts.color,
        'disk_type': parts.disk_type,
    }
    for key, parsed_value in fields.items():
        if parsed_value and (key in DISK_TITLE_WINS or not row_item.get_field(key)):
            row_item.set_field(key, parsed_value)


def _fasteners(text: str) -> tuple[str, str]:
    """Число отверстий и PCD: ``10x335``; иначе ``10 26мм ... раст.335`` или ``10 отв.``."""
    for pair in _PAIR.finditer(text):
        holes, pcd = pair.groups()
        if holes in _SLOTS and float(pcd) >= _MIN_PCD:
            return holes, pcd
    slots = _first_group(_HOLES_HOLE_SIZE, text) or _first_group(_HOLES_WORD, text)
    return slots, _first_group(_PCD_WORD, text)


def _thickness(text: str) -> str:
    """Толщина: ``(13мм)`` или голое ``16мм`` (кроме диаметра отверстия после числа отверстий)."""
    paren = _first_group(_THICKNESS_PAREN, text)
    return paren or _first_group(_THICKNESS_BARE, _HOLES_HOLE_SIZE.sub(' ', text))


def _first_known(text: str, known: Mapping[str, str]) -> str:
    """Значение для первого слова названия, известного справочнику (скобки вокруг слова не мешают)."""
    for token in text.split():
        found = known.get(token.strip('()').lower())
        if found:
            return found
    return ''


def _first_group(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match[1] if match else ''
