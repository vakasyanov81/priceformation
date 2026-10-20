"""tests for shared nomenclature title composition."""

from typing import Any

import pytest

from domain.row_item.row_item import RowItem
from parsers.nomenclature_brand import brand_label, model_label
from parsers.nomenclature_title import (
    TireTitleTokens,
    compose_tire_title,
    join_size_parts,
    join_title_parts,
    load_velocity,
)


def _row(**fields: Any) -> RowItem:
    return RowItem(fields)


@pytest.mark.parametrize(
    ('parts', 'expected'),
    [
        (('205/55R16', 'Kama', 'Euro'), '205/55R16 Kama Euro'),
        (('205/55R16', '', 'Euro'), '205/55R16 Euro'),
        (('205/55R16', None, '  '), '205/55R16'),
    ],
)
def test_join_title_parts_skips_empty(parts: tuple[object, ...], expected: str) -> None:
    assert join_title_parts(*parts) == expected


@pytest.mark.parametrize(
    ('parts', 'expected'),
    [
        (('205', '/55', 'R16'), '205/55R16'),
        (('30', 'x', '9.5', 'R', '15'), '30x9.5R15'),
        (('30', '/', '', 'R', '15'), '30/R15'),
        (('11', '.00', '', 'R20'), '11.00R20'),
    ],
)
def test_join_size_parts_skips_empty(parts: tuple[object, ...], expected: str) -> None:
    assert join_size_parts(*parts) == expected


def test_brand_label_keeps_brand_case() -> None:
    """Регистр бренда как в поле: `XCMG` не превращается в `Xcmg`, `BFGoodrich` в `Bfgoodrich`."""
    assert brand_label(_row(manufacturer_name='XCMG')) == 'XCMG'
    assert brand_label(_row(manufacturer_name='BFGoodrich')) == 'BFGoodrich'
    assert brand_label(_row(manufacturer_name=' Royal Spin ')) == 'Royal Spin'
    assert brand_label(_row()) == ''


@pytest.mark.parametrize(
    ('brand', 'model', 'expected'),
    [
        ('Ikon', 'Ikon Character Eco C2', 'Character Eco C2'),
        ('Кама', 'КАМА-NF 701', 'NF 701'),
        ('Cordiant', 'CORDIANT PROFESSIONAL DR-1', 'PROFESSIONAL DR-1'),
        ('LS', 'LS FG10', 'FG10'),
        ('Кама', 'Камаз-5', 'Камаз-5'),
        ('KN', 'KN1061', 'KN1061'),
        ('Кама', 'Кама', 'Кама'),
        ('', 'Ikon Character', 'Ikon Character'),
    ],
)
def test_model_label_drops_leading_brand(brand: str, model: str, expected: str) -> None:
    """Бренд в начале модели не повторяется в title; слитное начало и пустой остаток модель не трогают."""
    assert model_label(_row(manufacturer_name=brand, model=model)) == expected


def test_load_velocity_concatenates() -> None:
    assert load_velocity(_row(index_load='94', index_velocity='W')) == '94W'
    assert load_velocity(_row(index_load='94')) == '94'
    assert load_velocity(_row()) == ''


def test_tire_title_tokens_put_xl_after_load_velocity() -> None:
    """XL стоит сразу за нагрузкой и скоростью, перед `<N>PR` и камерностью."""
    tokens = TireTitleTokens(
        '205/55R16', 'Kumho', 'WinterCraft', load_velocity='94T', xl='XL', layering='8', camera='TT'
    )

    assert tokens.compose() == '205/55R16 Kumho WinterCraft 94T XL 8PR TT'


def test_compose_tire_title_canonical_order() -> None:
    """Порядок: размер, бренд, модель, нагрузка+скорость, после неё доп. токены, `<N>PR`, камера, RunFlat, ось."""
    row = _row(
        manufacturer_name='Pirelli',
        model='P Zero',
        layering='PR16',
        index_load='103',
        index_velocity='Y',
    )

    title = compose_tire_title(
        row,
        '235/40R18',
        camera='TL',
        axis='рул.ось',
        after_load=('XL',),
        run_flat='RunFlat',
    )

    assert title == '235/40R18 Pirelli P Zero 103Y XL 16PR TL RunFlat Рулевая'


def test_compose_tire_title_keeps_xl_and_season_marks() -> None:
    """`XL`, `M+S` и `3PMSF` берутся из названия поставщика и надписи на боковине; `M+S` стоит сразу за камерностью."""
    row = _row(
        title='245/45ZR17 99W XL Ingens A1 TL M+S',
        inscription_on_the_side='3PMSF',
        manufacturer_name='Antares',
        model='Ingens A1',
        index_load='99',
        index_velocity='W',
    )

    assert compose_tire_title(row, '245/45ZR17', camera='TL') == '245/45ZR17 Antares Ingens A1 99W XL TL M+S 3PMSF'
