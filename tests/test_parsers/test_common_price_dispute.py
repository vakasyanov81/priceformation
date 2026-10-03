"""Явный конфликт шипа и сезона в группе дублей."""

from typing import Any

import pytest

from domain.row_item.row_item import RowItem
from parsers.common_price_dispute import dispute_note


def _rows(*rows: tuple[Any, Any]) -> list[RowItem]:
    """Строки из пар (шип, сезон)."""
    return [RowItem({'spike': spike, 'season': season}) for spike, season in rows]


@pytest.mark.parametrize(
    ('canon', 'raw'),
    [
        ('да', 'да'),
        ('да', 'yes'),
        ('да', 'Ш.'),
        ('да', ' да '),
        ('нет', 'нет'),
        ('нет', 'no'),
        ('', 'вытянут'),
        ('', None),
    ],
)
def test_spike_synonyms(canon: str, raw: Any) -> None:
    """Синонимы шипа приводятся к канону; неизвестное значение конфликта не даёт."""
    expected = 'шип' if canon == 'да' else ''
    assert dispute_note(_rows((raw, None), ('нет', None))) == expected


@pytest.mark.parametrize(
    ('canon', 'raw', 'expected'),
    [
        ('зимняя', 'зима', 'сезон'),
        ('зимняя', 'ЗИМНЯЯ', 'сезон'),
        ('летняя', 'лето', ''),
        ('летняя', 'Летняя ', ''),
        ('межсезонье', 'межсезонье', 'сезон'),
    ],
)
def test_season_synonyms(canon: str, raw: Any, expected: str) -> None:
    """Синонимы сезона приводятся к канону, неизвестный сезон сохраняется как есть."""
    assert dispute_note(_rows((None, raw), (None, 'лето'))) == expected


def test_spike_conflict() -> None:
    """шип «да» против «нет» — метка конфликта."""
    assert dispute_note(_rows(('да', None), ('нет', None))) == 'шип'


def test_spike_synonyms_do_not_conflict() -> None:
    """«да» и «ш.» — один канон, конфликта нет."""
    assert dispute_note(_rows(('да', None), ('Ш.', None))) == ''


def test_season_conflict() -> None:
    """зимняя против летней — метка конфликта."""
    assert dispute_note(_rows((None, 'зима'), (None, 'лето'))) == 'сезон'


def test_same_values_do_not_conflict() -> None:
    """одинаковые значения конфликта не дают."""
    assert dispute_note(_rows(('да', 'зима'), ('да', 'зима'))) == ''


def test_blank_values_do_not_conflict() -> None:
    """пустые значения отфильтровываются и не считаются разными."""
    rows = _rows(('да', 'зима'), (None, None), ('', ''))
    assert dispute_note(rows) == ''


def test_unknown_season_still_conflicts() -> None:
    """неизвестный сезон сравнивается как есть: «межсезонье» против «зима» — конфликт."""
    assert dispute_note(_rows((None, 'межсезонье'), (None, 'зима'))) == 'сезон'


def test_both_markers_joined() -> None:
    """оба конфликта в одной группе: метки соединяются запятой, шип идёт первым."""
    assert dispute_note(_rows(('да', 'зима'), ('нет', 'лето'))) == 'шип, сезон'
