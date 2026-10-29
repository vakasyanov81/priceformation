"""Каноническое написание токенов названия шины."""

import pytest

from parsers.nomenclature.labels import (
    axis_label,
    camera_label,
    layering_label,
    run_flat_label,
    season_marks_label,
    xl_label,
)

type _Sources = tuple[str | None, ...]


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
    ('raw', 'expected'),
    [
        ('tt', 'TT'),
        ('TL', 'TL'),
        ('TT', 'TT'),
        ('Цельнолитая', 'Цельнолитая'),
    ],
)
def test_camera_label(raw: str, expected: str) -> None:
    """Камерность заглавными, `TL` не отбрасывается (Р2); прочие пометки остаются как есть."""
    assert camera_label(raw) == expected


@pytest.mark.parametrize(
    ('sources', 'expected'),
    [
        (('245/45ZR17 99W XL Ingens A1 TL M+S', None), ('M+S',)),
        (('215/70R16 Geolandar TL M+S 3PMSF',), ('M+S', '3PMSF')),
        (('3PMSF', 'm&s'), ('M+S', '3PMSF')),
        (('Geolandar A/T G015 MS', 'XL'), ()),
        ((None, ''), ()),
    ],
)
def test_season_marks_label(sources: _Sources, expected: tuple[str, ...]) -> None:
    """`M+S`/`3PMSF` из любого из текстов, в каноническом порядке."""
    assert season_marks_label(*sources) == expected


@pytest.mark.parametrize(
    ('sources', 'expected'),
    [
        (('Ingens A1 XL TL',), 'XL'),
        (('Ingens', 'xl'), 'XL'),
        (('Ingens XLR',), ''),
        ((None,), ''),
    ],
)
def test_xl_label(sources: _Sources, expected: str) -> None:
    """`XL` отдельным словом хотя бы в одном тексте."""
    assert xl_label(*sources) == expected


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


@pytest.mark.parametrize(
    ('flag', 'title', 'expected'),
    [
        ('да', '', 'RunFlat'),
        (None, '245/35R21 Hankook Ventus S1 evo3 Run-Flat 96Y', 'RunFlat'),
        (None, '245/35R21 Hankook RunFlat 96Y', 'RunFlat'),
        (None, '245/35R21 Hankook Run Flat 96Y', 'RunFlat'),
        (None, '245/35R21 Hankook RFT 96Y', 'RunFlat'),
        ('нет', '245/35R21 Hankook Ventus 96Y', ''),
        (None, None, ''),
    ],
)
def test_run_flat_label(flag: object, title: str | None, expected: str) -> None:
    """RunFlat: колонка прайса «да» или маркер в названии (`RFT`, `Run Flat`, `Run-Flat`)."""
    assert run_flat_label(flag, title) == expected
