"""Признаки из названия для ключа группировки: вентиль, модель камеры и ободной ленты."""

import re

from domain.row_item.row_item import RowItem

_DISK_KIND = 'диск'
_TUBE_KINDS = ('камер', 'лент')
_VALVE_RE = re.compile(r'(?<![\w])с\s+вент', re.IGNORECASE)
# Модель камеры: `ГК-145`, `УК-13М` (и `УК-13 М`), `РК-5А-145`, `УК-14-02`; у ободной ленты — `300-508А`.
_CAMERA_MODEL_RE = re.compile(r'(?<![\w-])([А-ЯЁ]{1,3}-\d+(?:\s?[А-ЯЁ](?![\wа-яё]))?(?:-\d+)*)', re.IGNORECASE)
_RIM_TAPE_MODEL_RE = re.compile(r'(?<![\w.-])(\d{3}-\d{3}[А-ЯЁ])(?![\wа-яё])', re.IGNORECASE)


def _kind(row_item: RowItem) -> str:
    return (row_item.vendor.type_production or '').lower()


def valve_key(row_item: RowItem) -> str:
    """`с вент` — шина/камера «с вентилем»; у дисков вентиль уже в хвостах названия."""
    if _DISK_KIND in _kind(row_item):
        return ''
    return 'с вент' if has_valve(row_item.identity.title) else ''


def has_valve(title: str | None) -> bool:
    """В названии указан вентиль (`с вентилем`)."""
    return bool(_VALVE_RE.search(title or ''))


def tube_model(row_item: RowItem) -> str:
    """Модель камеры или ободной ленты из названия; пусто, если не указана или это не камера."""
    kind = _kind(row_item)
    if not any(tube_kind in kind for tube_kind in _TUBE_KINDS):
        return ''
    return tube_model_from_title(row_item.identity.title, is_rim_tape='лент' in kind)


def tube_model_from_title(title: str | None, *, is_rim_tape: bool) -> str:
    """Модель камеры (`ГК-145`) или ободной ленты (`300-508А`) из названия; пусто, если не указана."""
    pattern = _RIM_TAPE_MODEL_RE if is_rim_tape else _CAMERA_MODEL_RE
    match = pattern.search(title or '')
    return ''.join(match[1].split()).upper() if match else ''
