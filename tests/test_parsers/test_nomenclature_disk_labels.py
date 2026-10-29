"""Каноническое написание токенов названия диска."""

import pytest

from parsers.nomenclature.disk_labels import color_label


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('графит', 'Графит'),
        ('Хай вэй', 'Хай вэй'),
        ('дарк платинум', 'Дарк платинум'),
        ('BL', 'BL'),
        ('', ''),
        (None, ''),
    ],
)
def test_color_label(raw: object, expected: str) -> None:
    assert color_label(raw) == expected
