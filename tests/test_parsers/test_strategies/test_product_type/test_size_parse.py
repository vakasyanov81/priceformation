"""Разбор формы размера и пороги семейств классификатора (README §4–§5).

`_parse_title_size` сверяется целиком: форма и все её поля, а не только итоговый
тип — иначе выпадение ширины или сдвиг группы регулярки не наблюдаемы.
"""

from __future__ import annotations

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies import product_type as ptc
from parsers.strategies import product_types as pt

LIGHT_TRUCK = pt.LIGHT_TRUCK
MOTO = pt.MOTO
PASSENGER = pt.PASSENGER
SPECIAL = pt.SPECIAL
TRUCK = pt.TRUCK

_CLASSIFIER = ptc.ProductTypeClassifier()


@pytest.mark.parametrize(
    ('tech', 'expected'),
    [
        ('205/55/16', ptc._Metric(width=205, diameter=16, profile=55)),
        ('265/70/19.5', ptc._Metric(width=265, diameter=19.5, profile=70)),
        ('205/55r16', ptc._Metric(width=205, diameter=16, profile=55)),
        ('315/80-22.5', ptc._Metric(width=315, diameter=22.5, profile=80)),
        ('205/65r16c', ptc._Metric(width=205, diameter=16, profile=65, commercial=True)),
        ('31x10.5r15', ptc._Flotation(diameter=15)),
        ('24x10-11', ptc._Flotation(diameter=11)),
        ('18*7-8', ptc._Dash(width_raw='7', diameter=8)),
        ('37x12.50-16lt', ptc._Flotation(diameter=16, commercial=True)),
        ('165 r13', ptc._WidthOnly(diameter=13)),
        ('195 r17.5', ptc._WidthOnly(diameter=17.5)),
        ('185 r14c', ptc._WidthOnly(diameter=14, commercial=True)),
        ('7.50r16', ptc._Inch(width=7.5, diameter=16)),
        ('6.50r16c', ptc._Inch(width=6.5, diameter=16, commercial=True)),
        ('16.9/14-30', ptc._SpecialForm()),
        ('10.0/75-15.3', ptc._SpecialForm()),
        ('9.5lr15', ptc._SpecialForm()),
        ('11.00-20', ptc._Dash(width_raw='11.00', diameter=20)),
        ('18.4-26', ptc._Dash(width_raw='18.4', diameter=26)),
        ('без размера', None),
    ],
    ids=[
        'metric2',
        'metric2-decimal',
        'metric',
        'metric-dash',
        'metric-c',
        'flotation',
        'flotation-small-rim',
        'flotation-one-digit-rim',
        'flotation-lt',
        'width-only',
        'width-only-decimal',
        'width-only-c',
        'inch',
        'inch-c',
        'slash-dash',
        'slash-dash-decimal',
        'agro-lr',
        'dash',
        'dash-one-decimal',
        'none',
    ],
)
def test_parse_title_size(tech: str, expected: object) -> None:
    """Каждая форма размера разбирается в свою структуру со всеми полями."""
    assert ptc._parse_title_size(tech) == expected


def _classify(title: str, **fields: str) -> str:
    return _CLASSIFIER.classify(RowItem({'title': title, **fields}))


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('11.00-17.5', TRUCK),
        ('11.00-24', TRUCK),
        ('11.00-24.5', SPECIAL),
        ('11.00-16', SPECIAL),
        ('9.00-20', SPECIAL),
        ('11.0-20', SPECIAL),
        ('10.00-20', TRUCK),
    ],
    ids=['rim-min', 'rim-max', 'rim-above', 'rim-below', 'narrow', 'one-decimal', 'width-min'],
)
def test_dash_truck_bounds(title: str, expected: str) -> None:
    """Грузовая диагональ: ширина `dd.dd` от 10, посадочный 17.5–24 включительно."""
    assert _classify(title) == expected


@pytest.mark.parametrize(
    'title',
    ['10.0/75-15.3 Нортек', '9.5LR15 Нортек', '16.9/14-30'],
    ids=['slash-dash-small-rim', 'agro-lr', 'slash-dash-big-rim'],
)
def test_special_forms(title: str) -> None:
    """Формы `N/N-N` и `NLR N` — спецшина при любом посадочном диаметре."""
    assert _classify(title) == SPECIAL


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('185 R14 14PR', TRUCK),
        ('185 R14 PR14', TRUCK),
        ('185 R14 13PR', PASSENGER),
        ('6.50R16 13PR', SPECIAL),
        ('205/75R16 121A6 14PR', PASSENGER),
        ('205/75R16 121A6 13PR', SPECIAL),
    ],
    ids=['width-only-14', 'width-only-pr-after', 'width-only-13', 'inch-13', 'agro-index-14', 'agro-index-13'],
)
def test_truck_pr_bound(title: str, expected: str) -> None:
    """Слойность от 14PR — грузовая; ниже — не влияет; агро-индекс снимается грузовым PR."""
    assert _classify(title) == expected


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('130/70R17', MOTO),
        ('130/60R17', PASSENGER),
        ('140/70R17', PASSENGER),
        ('130/70R18', PASSENGER),
    ],
    ids=['moto', 'low-profile', 'wide', 'big-rim'],
)
def test_moto_bounds(title: str, expected: str) -> None:
    """Мотошина по размеру: ширина ≤ 130, посадочный ≤ 17, профиль ≥ 70."""
    assert _classify(title) == expected


@pytest.mark.parametrize(
    ('fields', 'expected'),
    [
        ({'width': '120', 'height_percent': '70', 'diameter': '17'}, MOTO),
        ({'width': '120', 'diameter': '17'}, PASSENGER),
        ({'width': '315', 'diameter': '20'}, PASSENGER),
    ],
    ids=['moto-profile', 'moto-no-profile', 'truck-no-profile'],
)
def test_unknown_profile_is_not_bound(fields: dict[str, str], expected: str) -> None:
    """Неизвестный профиль (размер из полей) не проходит ни мото-, ни грузовой порог."""
    assert _classify('Nortec без формы', **fields) == expected


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('130/70R17', LIGHT_TRUCK),
        ('11.00-20', TRUCK),
        ('11.00-16', SPECIAL),
        ('31x10.5R15', LIGHT_TRUCK),
    ],
    ids=['metric', 'dash-truck', 'dash-special', 'flotation'],
)
def test_declared_commercial_by_form(title: str, expected: str) -> None:
    """Маркер C в поле поставщика делает шину легкогрузовой; диагональ он не меняет."""
    assert _classify(title, tire_type='C') == expected


def test_decimal_comma_in_size() -> None:
    """Десятичная запятая в размере доходит до разбора точкой (через normalize_text)."""
    assert _classify('31x10,5R15') == PASSENGER
    assert _classify('37X12,50-16LT') == LIGHT_TRUCK
