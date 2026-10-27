"""Размер шины four_tochki sheet 1: добор полей из названия API и подготовка размера для сборки названия."""

from __future__ import annotations

import re

from domain.row_item.row_item import RowItem
from domain.row_item.row_item_casts import get_try_to_int_or_str
from parsers.strategies._four_tochki_tire_kind import is_special_tire, is_truck_tire
from parsers.strategies._tire_size_parts import TRAILING_ZEROS
from parsers.strategies._tire_title_fill import fill_tire_fields
from parsers.strategies._tire_title_parser import parse_tire_title

_PROFILE_L = 'L'
_DASH = '-'
_METRIC_WIDTH_MIN = 100
_L_FROM_EXCEL = f'{_PROFILE_L}.0'
# Конструкция, как её пишет разбор названия API (колонка `construction_type` у xlsx — `R`, `—`, `ZR`).
_DIAGONAL_PARSED = 'диагональная'
# Размер, который общий разбор названия не принимает: `ZR` (радиальная с ZR), префиксы `P`/`LT`.
_SIZE_PREFIX = re.compile(r'^(?:P|LT)(?=\d)')
_ZR_SIZE = re.compile(r'^(\S*?)ZR(?=\d)', re.IGNORECASE)
# Альтернативный размер в скобках сразу за размером (`11,00R20(300R508)`) и ободная запись (`6,00-9/4,00E`).
_ALT_AFTER_SIZE = re.compile(r'^(\S+?)\([^)]*\)')
_RIM_AFTER_SIZE = re.compile(r'^(\d+(?:[.,]\d+)?-\d+(?:[.,]\d+)?)/\d+(?:[.,]\d+)?[A-Z]?(?=\s|$)')
# Скорость в скобках после индекса нагрузки: `94(Y)`; в прайсе она записана так же, со скобками.
_SPEED_PAREN = re.compile(r'(\d)\(([A-Za-z])\)(?=\s|$)')
# Суффикс диаметра в размере названия: `185/75R16C`, `7.50R16LT`.
_SIZE_SUFFIX = re.compile(r'^\S*?\d(?P<suffix>LT|C)(?=\s|$)')


def fill_size_from_title(row_item: RowItem) -> None:
    """Размер API, который общий разбор не принял (`245/45ZR17`, `P225/60R18`): разобрать без `ZR`/`P`."""
    if row_item.tire.width or not row_item.identity.title:
        return
    text = _strip_size_noise(row_item.identity.title)
    speed = _SPEED_PAREN.search(text)
    text = _SPEED_PAREN.sub(r'\1\2', text)
    parts = parse_tire_title(_ZR_SIZE.sub(r'\1R', text, count=1))
    if parts is None:
        return
    fill_tire_fields(row_item, parts)
    if _ZR_SIZE.match(text):
        diameter = parts.size.diameter
        row_item.set_field('diameter', f'ZR{diameter}')
    if speed is not None:
        letter = speed[2]
        row_item.set_field('index_velocity', f'({letter})')


def fill_size_suffix(row_item: RowItem) -> None:
    """Суффикс диаметра из названия API (`C`, `LT`) в поле диаметра, как в колонке прайса (`R13C`).

    Название собирается дважды (при обогащении и в шаге pipeline), поэтому суффикс дописываем
    только если диаметр его ещё не содержит: при повторной сборке дубля не будет.
    """
    match = _SIZE_SUFFIX.match(row_item.identity.title or '')
    diameter = str(row_item.tire.diameter or '')
    if match is None or not diameter or diameter.endswith(match['suffix']):
        return
    suffix = match['suffix']
    row_item.set_field('diameter', f'{diameter}{suffix}')


def prepare_dimensions(row_item: RowItem) -> tuple[str, str, str, str]:
    """Ширина, профиль, диаметр и тип конструкции."""
    width = _canon(row_item.tire.width)
    height = _canon(row_item.tire.height_percent).replace('999', _PROFILE_L)
    height = height.replace(_L_FROM_EXCEL, _PROFILE_L)
    diameter = str(row_item.tire.diameter or '').replace('—', _DASH)
    diameter = diameter.replace(',', '.').replace('R', '')
    construct = 'R'
    if _DASH in diameter:
        construct = _DASH
        diameter = diameter.replace(_DASH, '')
    if row_item.tire.construction_type == _DIAGONAL_PARSED:
        construct = _DASH
    return width, height, diameter, construct


def resolve_width_postfix(row_item: RowItem, width: str, height_percent: str, diameter: str) -> str:
    """Подбирает суффикс ширины для title."""
    if height_percent == _PROFILE_L:
        return height_percent
    if _special_inch_dot(row_item, width, height_percent):
        return '.0'
    if width == '10' and diameter == '20':
        return '.00'
    skip_truck_dot = diameter in {'22.5', '16'} or height_percent or '.' in width
    if not is_truck_tire(row_item) or skip_truck_dot:
        return ''
    return '.00'


def _strip_size_noise(title: str) -> str:
    """Название без префикса `P`/`LT`, размера в скобках и ободной записи сразу за размером."""
    text = _SIZE_PREFIX.sub('', title.strip(), count=1)
    text = _ALT_AFTER_SIZE.sub(r'\1', text, count=1)
    return _RIM_AFTER_SIZE.sub(r'\1', text, count=1)


def _canon(raw: object) -> str:
    """Число без запятой и лишних нулей: `10,50` → `10.5`."""
    text = str(raw or '').replace(',', '.')
    number = str(get_try_to_int_or_str(text))
    return TRAILING_ZEROS.sub(r'\1', number)


def _special_inch_dot(row_item: RowItem, width: str, height_percent: str) -> bool:
    """Нужен суффикс .0 для дюймовой спецшины, не для метрики 140/55."""
    if not is_special_tire(row_item) or not height_percent:
        return False
    if height_percent == _PROFILE_L or not width.isdigit():
        return False
    return int(width) < _METRIC_WIDTH_MIN
