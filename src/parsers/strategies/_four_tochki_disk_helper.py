"""
Title extras for four_tochki sheet 2 disks.

Вынесено из ``src/parsers/vendors/four_tochki/four_tochki_disk_title.py`` —
чистый перенос без изменений, чтобы удалить легаси-модуль.
"""

from __future__ import annotations

import re
from typing import Any

from domain.row_item.disk_name_extras import disk_name_extras
from domain.row_item.row_item import RowItem
from parsers.nomenclature_title import join_title_parts

_THICKNESS_RE = re.compile(r'\((\d+(?:[.,]\d+)?)\s*мм\)', re.IGNORECASE)


def thickness_from_name(name: str) -> str:
    """Толщина из скобок в наименовании: (15,5 мм)."""
    match = _THICKNESS_RE.search(name)
    if not match:
        return ''
    return match.group(1).replace(',', '.')


def fill_disk_thickness(row_item: RowItem) -> None:
    """Заполнить толщину из исходного наименования, если колонка пуста."""
    if row_item.disk.disk_thickness:
        return
    thickness = thickness_from_name(row_item.identity.title or '')
    if thickness:
        row_item.set_field('disk_thickness', thickness)


def disk_name_suffix(name: str, model: str = '') -> str:
    """Толщина, усиление, камерность и различающие хвосты из наименования; скобки модели не повторяются."""
    thickness = thickness_from_name(name)
    thick_label = f'({thickness} мм)' if thickness else ''
    return join_title_parts(
        thick_label,
        'усил.' if 'усил' in name.lower() else '',
        _tube_label(name),
        disk_name_extras(name, model),
    )


def et_label(eet: Any) -> str:
    """ET с нулём: 0 не должен пропадать как falsy."""
    if eet is None or eet == '':
        return 'ET'
    return f'ET{eet}'


def disk_diameter(raw: Any) -> str:
    """Диаметр без хвостового .0, без порчи 22.5."""
    text = str(raw or '')
    if text.endswith('.0'):
        return text[:-2]
    return text


def disk_width(raw: Any) -> str:
    """Ширина с десятичной частью, как в прайсе: `7` → `7.0`, `6.75` без изменений."""
    text = str(raw or '')
    return f'{text}.0' if text.isdigit() else text


def _tube_label(name: str) -> str:
    lowered = name.lower()
    if 'под камеру' in lowered:
        return 'под камеру'
    if 'б/к' in lowered:
        return 'б/к'
    return ''
