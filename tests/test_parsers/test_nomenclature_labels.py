"""Каноническое написание токенов названия шины."""

import pytest

from parsers.nomenclature_labels import axis_label, camera_label, layering_label


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('16', '16PR'),
        ('16PR', '16PR'),
        ('PR16', '16PR'),
        ('16 PR', '16PR'),
        ('', ''),
        (None, ''),
        ('XL', ''),
    ],
)
def test_layering_label(raw: object, expected: str) -> None:
    assert layering_label(raw) == expected


@pytest.mark.parametrize(
    ('raw', 'keep_tl', 'expected'),
    [
        ('tt', True, 'TT'),
        ('TL', True, 'TL'),
        ('TL', False, ''),
        ('TT', False, 'TT'),
        ('Цельнолитая', False, 'Цельнолитая'),
    ],
)
def test_camera_label(raw: str, keep_tl: bool, expected: str) -> None:
    """`TL` у легковых не пишется (Р2), прочие камерности и пометки остаются."""
    assert camera_label(raw, keep_tl=keep_tl) == expected


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('вед.ось', 'Ведущая'),
        ('Рулевая', 'Рулевая'),
        ('руль/ прицеп', 'Рулевая'),
        ('унив.ось', 'Универсальная'),
        ('приц.', 'Прицепная'),
        ('карьер', 'Карьерная'),
        ('шашка', ''),
        (None, ''),
    ],
)
def test_axis_label(raw: object, expected: str) -> None:
    assert axis_label(raw) == expected
