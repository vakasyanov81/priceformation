"""
Title builders for four_tochki sheet 1 tires.

Вынесено из ``src/parsers/vendors/four_tochki/four_tochki_title.py`` и
``four_tochki_title_parts.py`` — чистый перенос без изменений, чтобы удалить
легаси-модули. Тип шины — ``_four_tochki_tire_kind``, размер — ``_four_tochki_tire_size``.
"""

from __future__ import annotations

import re

from domain.row_item.row_item import RowItem
from parsers.nomenclature_labels import camera_label, run_flat_label
from parsers.nomenclature_title import compose_tire_title, join_size_parts
from parsers.strategies._four_tochki_tire_kind import is_special_tire, is_truck_tire
from parsers.strategies._four_tochki_tire_size import (
    fill_size_from_title,
    fill_size_suffix,
    prepare_dimensions,
    resolve_width_postfix,
)

_PROFILE_L = 'L'
# Камера: `TL`, `TT (только шина)`, либо цельнолитая пометка вместо камеры (`Цельнолитая с бортом`).
_CAMERA = re.compile(
    r'(?<!\S)(?:TT|TL|TTF|TT/TL|TL/TT)(?:\s*\(только шина\))?(?=\s|$)'
    r'|(?<!\S)Цельнолитая(?: немаркая)?(?: с бортом)?(?=\s|$)',
    re.IGNORECASE,
)


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
    fill_size_from_title(row_item)
    fill_size_suffix(row_item)
    if not row_item.tire.width and row_item.identity.title:
        return row_item.identity.title
    dims = prepare_dimensions(row_item)
    return _compose_title(row_item, dims).strip()


def _compose_title(row_item: RowItem, dims: tuple[str, str, str, str]) -> str:
    """Собрать title по типу шины. dims: width, height_raw, diameter, construct."""
    height = f'/{dims[1]}'
    if not dims[1] or dims[1] == _PROFILE_L:
        height = ''
    postfix = resolve_width_postfix(row_item, dims[0], dims[1], dims[2])
    construct_diameter = f'{dims[3]}{dims[2]}'.replace('RZ', 'ZR')
    size = join_size_parts(dims[0], postfix, height, construct_diameter)
    if is_truck_tire(row_item):
        return truck_title(row_item, size)
    if row_item.tire.ext_diameter:
        size = join_size_parts(row_item.tire.ext_diameter, 'x', dims[0], construct_diameter)
        return ext_diameter_title(row_item, size)
    return default_tire_title(row_item, size)


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
