"""Год выпуска шины по названию."""

import pytest

from domain.row_item.production_year import OLDEST_YEAR, production_year


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('175/65R14 Viatti Brina V-521 82T 2023г.в.', 2023),
        ('215/70R16 Cordiant Winter Drive PW-1 100T 2021 г.в.', 2021),
        ('225/55R17 Pirelli Ice Zero 101T XL шип 2022 г.в.', 2022),
        ('175/65R14 Formula ICE 82T шип (2 года и старше)', OLDEST_YEAR),
        ('175/65R14 Viatti Brina V-521 82T', None),
        ('Диск 5.5x16 6x170 ET2023', None),
        ('', None),
        (None, None),
    ],
)
def test_production_year(title: str | None, expected: int | None) -> None:
    assert production_year(title) == expected
