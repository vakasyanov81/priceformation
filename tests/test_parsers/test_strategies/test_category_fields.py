"""Стратегия полей по категории-размеру названия (`category.size_fields`)."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies.category_fields import CategoryFields

_MAPPING = {'Грузовая шина': {'season': 'Всесезонная'}, 'Спецшина': {'season': 'Всесезонная'}}


@pytest.mark.parametrize(
    'title',
    [
        '10.00 R20 DOUBLEROAD DR-801 18PR унив.ось',
        '12.4L-16 Бел-160М 8PR сельхозшина',
        '17.5-25 Rockbuster H108A E3/L3 28PR спецшина',
    ],
)
def test_category_fields_sets_season_for_truck_and_special(title: str) -> None:
    """Грузовые и спецшины получают сезон из конфига."""
    row = RowItem({'title': title})

    CategoryFields(_MAPPING).apply(row)

    assert row.tire.season == 'Всесезонная'


@pytest.mark.parametrize(
    'title',
    [
        '175/70 R13 КАМА ALGA НК-531',
        '185/75 R16C Кама НК-243 104/102Q',
        'Диск штамп NORTEC-16 11.75x22.5',
    ],
)
def test_category_fields_ignores_other_sizes(title: str) -> None:
    """Легковые и нешинные позиции сезон не получают."""
    row = RowItem({'title': title})

    CategoryFields(_MAPPING).apply(row)

    assert row.tire.season is None


def test_category_fields_keeps_existing_season() -> None:
    """Уже проставленный сезон не перетирается."""
    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 18PR унив.ось', 'season': 'Зимняя'})

    CategoryFields(_MAPPING).apply(row)

    assert row.tire.season == 'Зимняя'


def test_category_fields_empty_mapping_is_noop() -> None:
    """Пустая карта ничего не меняет."""
    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 18PR унив.ось'})

    CategoryFields({}).apply(row)

    assert row.tire.season is None
