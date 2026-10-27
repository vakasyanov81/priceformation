"""Запись разобранного названия шины в поля позиции."""

from __future__ import annotations

import re

from domain.row_item.row_item import RowItem
from parsers.strategies._tire_title_parser import TireTitleParts
from parsers.strategies._tire_title_usage import axis, spike
from parsers.strategies._title_wins import TIRE_TITLE_WINS

# Хвост, дописанный к обрезанной колонкой модели слитно: `A` в `AE-51A`, `+` в `NF201+`, `-1` в `Я-245-1`.
_MODEL_TAIL = re.compile(r'[\w+-]+')


def fill_tire_fields(row_item: RowItem, parts: TireTitleParts) -> None:
    """Записать разобранные параметры в поля позиции, не перетирая готовые."""
    for key, parsed_value in _parsed_fields(parts).items():
        current = row_item.get_field(key)
        if parsed_value and (not current or _title_wins(key, current, parsed_value)):
            row_item.set_field(key, parsed_value)


def _parsed_fields(parts: TireTitleParts) -> dict[str, str]:
    """Ключи полей позиции → значения из разобранного названия."""
    size = parts.size
    return {
        'width': size.width,
        'height_percent': size.height_percent,
        'diameter': size.diameter,
        'ext_diameter': size.ext_diameter,
        'construction_type': size.construction,
        'axis': axis(parts.usage),
        'layering': parts.layering,
        'index_load': parts.load,
        'index_velocity': parts.velocity,
        'spike': spike(parts.usage),
        'intimacy': parts.intimacy,
        'model': parts.model_name,
    }


def _title_wins(key: str, current: object, parsed: str) -> bool:
    """Значение из названия заменяет заполненное колонкой."""
    if key == 'model':
        return _completes_model(str(current), parsed)
    return key in TIRE_TITLE_WINS and _differs(current, parsed)


def _completes_model(column: str, parsed: str) -> bool:
    """Колонка обрезана: модель из названия — она же с приписанным слитно хвостом (`AE-51` → `AE-51A`)."""
    tail = parsed[len(column) :]
    if not parsed.lower().startswith(column.lower()):
        return False
    return _MODEL_TAIL.fullmatch(tail) is not None


def _differs(current: object, parsed: str) -> bool:
    """Значения разные без учёта регистра: `да` из конфига и `Да` из названия — одно и то же."""
    return str(current).strip().lower() != parsed.lower()
