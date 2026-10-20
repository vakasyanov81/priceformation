# flake8: noqa: WPS202
"""
Title builders for four_tochki sheet 1 tires.

Вынесено из ``src/parsers/vendors/four_tochki/four_tochki_title.py`` и
``four_tochki_title_parts.py`` — чистый перенос без изменений, чтобы удалить
легаси-модули.
"""

from __future__ import annotations

import re

from domain.row_item.row_item import RowItem
from domain.row_item.row_item_casts import get_try_to_int_or_str
from parsers.nomenclature_labels import camera_label, run_flat_label
from parsers.nomenclature_title import compose_tire_title, join_size_parts
from parsers.strategies._tire_title_parser import TRAILING_ZEROS, fill_tire_fields, parse_tire_title

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
# Камера: `TL`, `TT (только шина)`, либо цельнолитая пометка вместо камеры (`Цельнолитая с бортом`).
_CAMERA = re.compile(
    r'(?<!\S)(?:TT|TL|TTF|TT/TL|TL/TT)(?:\s*\(только шина\))?(?=\s|$)'
    r'|(?<!\S)Цельнолитая(?: немаркая)?(?: с бортом)?(?=\s|$)',
    re.IGNORECASE,
)
# Суффикс диаметра в размере названия: `185/75R16C`, `7.50R16LT`.
_SIZE_SUFFIX = re.compile(r'^\S*?\d(?P<suffix>LT|C)(?=\s|$)')


# Тип шины API → тип прайса xlsx (по парам позиций обоих источников): внедорожные и легкогрузовые —
# легковые, сельхоз и погрузчики — спецтехника, квадроциклы — мото.
_API_TIRE_TYPES = {
    'vned': 'легковая',
    'cartruck': 'легковая',
    'selhoz': 'спецтехника',
    'loader': 'спецтехника',
    'quadbike': 'мото',
}


def _tire_kind(row_item: RowItem) -> str:
    """Тип шины в нижнем регистре, как в прайсе xlsx."""
    raw = (row_item.tire.tire_type or '').lower()
    return _API_TIRE_TYPES.get(raw, raw)


def is_truck_tire(row_item: RowItem) -> bool:
    """Грузовая шина?"""
    return _tire_kind(row_item) == 'грузовая'


def is_special_tire(row_item: RowItem) -> bool:
    """Спецтехника?"""
    return _tire_kind(row_item) == 'спецтехника'


def get_prepared_title(row_item: RowItem) -> str:
    """
    1) Форточки:
    10-20 Armour TI300
    на
    10.00-20 Armour TI300 16PR TTF

    2). Форточки:
    10/75-15.3 Forerunner QH602 R-4
    на
    10.0/75-15.3 Forerunner QH602 R-4 12PR TL

    3) Форточки:
    11/999-15 Galaxy Rib Implement I-1
    на
    11L-15 Galaxy Rib Implement I-1 12PR TL

    4) МИМ:
    16.5/70R18 Белшина КФ-97 10 149A TTF
    на
    16.5/70-18 Белшина КФ-97 10 149A TTF
    :param item:
    :return:
    """
    _fill_size_from_title(row_item)
    _fill_size_suffix(row_item)
    if not row_item.tire.width and row_item.identity.title:
        return row_item.identity.title
    dims = _prepare_dimensions(row_item)
    return _compose_title(row_item, dims).strip()


def _fill_size_from_title(row_item: RowItem) -> None:
    """Размер API, который общий разбор не принял (`245/45ZR17`, `P225/60R18`): разобрать без `ZR`/`P`."""
    if row_item.tire.width or not row_item.identity.title:
        return
    text = _SIZE_PREFIX.sub('', row_item.identity.title.strip(), count=1)
    text = _ALT_AFTER_SIZE.sub(r'\1', text, count=1)
    text = _RIM_AFTER_SIZE.sub(r'\1', text, count=1)
    speed = _SPEED_PAREN.search(text)
    text = _SPEED_PAREN.sub(r'\1\2', text)
    radial_zr = _ZR_SIZE.match(text) is not None
    parts = parse_tire_title(_ZR_SIZE.sub(r'\1R', text, count=1))
    if parts is None:
        return
    fill_tire_fields(row_item, parts)
    if radial_zr:
        row_item.set_field('diameter', f'ZR{parts.size.diameter}')
    if speed is not None:
        row_item.set_field('index_velocity', f'({speed[2]})')


def _prepare_dimensions(row_item: RowItem) -> tuple[str, str, str, str]:
    """Ширина, профиль, диаметр и тип конструкции."""

    def canon(raw: object) -> str:
        text = str(raw or '').replace(',', '.')
        value = str(get_try_to_int_or_str(text))
        return TRAILING_ZEROS.sub(r'\1', value)

    width = canon(row_item.tire.width)
    height = canon(row_item.tire.height_percent).replace('999', _PROFILE_L)
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


def _compose_title(row_item: RowItem, dims: tuple[str, str, str, str]) -> str:
    """Собрать title по типу шины. dims: width, height_raw, diameter, construct."""
    height = f'/{dims[1]}'
    if not dims[1] or dims[1] == _PROFILE_L:
        height = ''
    postfix = _resolve_width_postfix(row_item, dims[0], dims[1], dims[2])
    construct_diameter = f'{dims[3]}{dims[2]}'.replace('RZ', 'ZR')
    size = join_size_parts(dims[0], postfix, height, construct_diameter)
    if is_truck_tire(row_item):
        return truck_title(row_item, size)
    if row_item.tire.ext_diameter:
        size = join_size_parts(row_item.tire.ext_diameter, 'x', dims[0], construct_diameter)
        return ext_diameter_title(row_item, size)
    return default_tire_title(row_item, size)


def _special_inch_dot(row_item: RowItem, width: str, height_percent: str) -> bool:
    """Нужен суффикс .0 для дюймовой спецшины, не для метрики 140/55."""
    if not is_special_tire(row_item) or not height_percent:
        return False
    if height_percent == _PROFILE_L or not width.isdigit():
        return False
    return int(width) < _METRIC_WIDTH_MIN


def _resolve_width_postfix(row_item: RowItem, width: str, height_percent: str, diameter: str) -> str:
    """подбирает суффикс ширины для title"""
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


# ---------------------------------------------------------------------------
# Title size format variants (ex-four_tochki_title_parts.py)
# ---------------------------------------------------------------------------


def _camera(row_item: RowItem) -> str:
    """Камерность колонки; если колонки нет — из названия (разбор кладёт только `TL`/`TT` в `intimacy`)."""
    if row_item.tire.camera_type:
        return str(row_item.tire.camera_type).strip()
    camera = _CAMERA.search(row_item.identity.title or '')
    if camera is not None:
        return ' '.join(camera.group(0).split())
    return str(row_item.tire.intimacy or '')


def _runflat(row_item: RowItem) -> str:
    """RunFlat из колонки прайса или из названия (`RFT`, `Run Flat`)."""
    return run_flat_label(row_item.tire.run_flat, row_item.identity.title)


def _fill_size_suffix(row_item: RowItem) -> None:
    """Суффикс диаметра из названия API (`C`, `LT`) в поле диаметра, как в колонке прайса (`R13C`).

    Название собирается дважды (при обогащении и в шаге pipeline), поэтому суффикс дописываем
    только если диаметр его ещё не содержит: при повторной сборке дубля не будет.
    """
    match = _SIZE_SUFFIX.match(row_item.identity.title or '')
    diameter = str(row_item.tire.diameter or '')
    if match is None or not diameter or diameter.endswith(match['suffix']):
        return
    row_item.set_field('diameter', f'{diameter}{match["suffix"]}')


def truck_title(row_item: RowItem, size: str) -> str:
    """Title для грузовой шины."""
    return compose_tire_title(
        row_item,
        size,
        camera=camera_label(_camera(row_item)),
        axis=row_item.tire.axis or '',
    )


def ext_diameter_title(row_item: RowItem, size: str) -> str:
    """Title с внешним диаметром."""
    return compose_tire_title(
        row_item,
        size,
        after_load=(row_item.tire.us_aff_designation,),
        run_flat=_runflat(row_item),
    )


def default_tire_title(row_item: RowItem, size: str) -> str:
    """Обычный title легковой/спец: ось — только у спецтехники."""
    special = is_special_tire(row_item)
    return compose_tire_title(
        row_item,
        size,
        camera=camera_label(_camera(row_item)),
        axis=row_item.tire.axis or '' if special else '',
        run_flat=_runflat(row_item),
    )
