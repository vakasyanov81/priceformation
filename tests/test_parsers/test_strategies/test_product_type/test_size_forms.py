"""Формы размера и границы семейств, не покрытые в `test_classify`.

Целится в конкретные ветви `_parse_title_size`/`_is_special`/`_*_family`,
которые иначе остаются выжившими мутантами (README §4–§5).
"""

from __future__ import annotations

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies import product_types as pt
from parsers.strategies.product_type import ProductTypeClassifier

DISK = pt.DISK
LIGHT_TRUCK = pt.LIGHT_TRUCK
O_RING = pt.O_RING
PASSENGER = pt.PASSENGER
SPECIAL = pt.SPECIAL
TRUCK = pt.TRUCK

_CLASSIFIER = ProductTypeClassifier()


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('265/70/19.5', TRUCK),
        ('175/70/14', PASSENGER),
        ('265/70R17 E3/L3', SPECIAL),
        ('125/80R15C', LIGHT_TRUCK),
        ('195 R17.5', TRUCK),
        ('165 R13', PASSENGER),
        ('6.50R16 16PR', TRUCK),
        ('250/70R20 100/100', TRUCK),
        ('345/80R24', SPECIAL),
        ('265/70R16 унив.ось', TRUCK),
        ('295/80R20', TRUCK),
        ('8.5x20 10x335 ET180 281 под камеру', DISK),
        ('Уплотнительное седло R25', ''),
        ('340/80R24', SPECIAL),
        ('185/60R13 104/102', LIGHT_TRUCK),
        ('225/45R17 104/102', LIGHT_TRUCK),
        ('225/45R18 104/102', PASSENGER),
        ('6.50R16 14PR', TRUCK),
        ('6.50R16 PR14', TRUCK),
        ('10.00R15', TRUCK),
        ('6.50R16', SPECIAL),
        ('7.00R16', TRUCK),
        ('11.00-17.5', TRUCK),
        ('11.00-24', TRUCK),
        ('Уплотнительное кольцо', O_RING),
        ('Кольцо R25', O_RING),
        ('Кольцо без размера', ''),
    ],
)
def test_size_forms_and_family_bounds(title: str, expected: str) -> None:
    """Разные формы размера и границы семейств дают ожидаемый тип."""
    assert _CLASSIFIER.classify(RowItem({'title': title})) == expected


@pytest.mark.parametrize(
    ('fields', 'expected'),
    [
        ({'width': '250', 'height_percent': '80', 'diameter': '20'}, TRUCK),
        ({'width': '315,5', 'height_percent': '80', 'diameter': '22,5'}, TRUCK),
        ({'width': '315', 'height_percent': '70', 'diameter': '20'}, TRUCK),
        ({'width': '205', 'height_percent': '55', 'diameter': '16'}, PASSENGER),
        ({'width': '205', 'height_percent': '55'}, ''),
    ],
)
def test_structured_fields_used(fields: dict[str, str], expected: str) -> None:
    """Профиль, ширина и десятичные запятые в полях доходят до семейства; без диаметра — нет."""
    row = RowItem({'title': 'Nortec без формы', **fields})
    assert _CLASSIFIER.classify(row) == expected
