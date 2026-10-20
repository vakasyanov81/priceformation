"""Завод-изготовитель шины по названию."""

import pytest

from domain.row_item.production_plant import production_plant


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('265/70R19.5 КАМА NT202 143/141J TL НкШЗ', 'НкШЗ'),
        ('11.00R20 И-68А 150/146K НКШЗ автошина', 'НкШЗ'),
        ('425/85R21 TYREX CRG POWER VO-1260 20PR 160J TT ОШЗ', 'ОШЗ'),
        ('315/70R22.5 CORDIANT PROFESSIONAL DR-1 154/150L TL ЯШЗ', 'ЯШЗ'),
        ('10.00R20 Кама 16PR волшз', 'ВолШЗ'),
        ('12.00R20 И-281 БШК', 'БШК'),
        ('175/65R14 Viatti Brina V-521 82T', None),
        ('175/65R14 Омскшина 82T', None),
        ('', None),
        (None, None),
    ],
)
def test_production_plant(title: str | None, expected: str | None) -> None:
    assert production_plant(title) == expected
