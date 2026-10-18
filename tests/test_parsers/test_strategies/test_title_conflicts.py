"""Сравнение значений колонки и названия при расхождении: число с запятой и точкой — одно число."""

import pytest

from parsers.strategies.title_conflicts import _canon

_EQUAL_PAIRS = [('40,5', '40.5'), (40, '40.0'), (' abc ', 'ABC')]


@pytest.mark.parametrize(('left', 'right'), _EQUAL_PAIRS)
def test_equal_values_have_same_canon(left: object, right: object) -> None:
    """Запятая и точка, int и строка с `.0`, регистр и пробелы значения не меняют."""
    assert _canon(left) == _canon(right)


def test_different_values_have_different_canon() -> None:
    """Разные числа остаются разными."""
    assert _canon('40.5') != _canon('40.6')
