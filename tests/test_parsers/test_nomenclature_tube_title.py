"""tests for tube and rim tape title composition."""

import pytest

from parsers.nomenclature.tube_title import compose_tube_title, tube_size_label


@pytest.mark.parametrize(
    ('size', 'expected'),
    [
        (('11.00', '', '20', ''), '11.00-20'),
        (('12.5', '80', '18', ''), '12.5/80-18'),
        (('175', '', '16', '', '185'), '175/185-16'),
        (('500', '', '508', '1200'), '1200x500-508'),
    ],
)
def test_tube_size_label(size: tuple[str, ...], expected: str) -> None:
    assert tube_size_label(*size) == expected


@pytest.mark.parametrize(
    ('is_rim_tape', 'brand', 'model', 'valve', 'expected'),
    [
        (False, '', '', False, 'Камера 11.00-20'),
        (False, 'ОШЗ', 'ГК-115', False, 'Камера 11.00-20 ОШЗ ГК-115'),
        (False, '', '', True, 'Камера 11.00-20 с вентилем'),
        (True, '', '', False, 'Ободная лента 11.00-20'),
        (True, 'Nortec', '300-508А', False, 'Ободная лента 300-508А Nortec'),
    ],
    ids=['plain', 'brand-and-model', 'valve', 'rim-tape', 'rim-tape-model-replaces-size'],
)
def test_compose_tube_title(is_rim_tape: bool, brand: str, model: str, valve: bool, expected: str) -> None:
    assert compose_tube_title(is_rim_tape, '11.00-20', brand, model, valve=valve) == expected
