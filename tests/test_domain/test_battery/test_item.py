"""Регрессии аккумуляторной модели на полях реального прайса plant."""

from collections.abc import Callable
from dataclasses import FrozenInstanceError, asdict, fields
from decimal import Decimal
from operator import setitem
from typing import Literal, assert_type

import pytest

from domain.battery.case import BatteryCase
from domain.battery.field_registry import FIELD_CONVERTERS, FIELD_KEYS
from domain.battery.identity import BatteryIdentity
from domain.battery.item import BatteryItem
from domain.battery.offer import BatteryOffer
from domain.battery.parameters import BatteryParameters
from domain.product_groups import ProductGroup
from domain.row_item.field_registry import FIELD_KEYS as TIRE_FIELDS


@pytest.fixture
def plant_fields() -> dict[str, object]:
    """Значения первой позиции plant; коды и артикулы намеренно различны."""
    return {
        'title': '   XTREME +EFB  100 обр (125D31L) ',
        'code': '0123247    ',
        'code_art': 'plnt0123247',
        'code_man': '125D31L',
        'manufacturer_name': 'Алькор (Тюмень)',
        'model': 'XTREME +EFB',
        'capacity_ah': 100.0,
        'starting_current_a': 850.0,
        'length_mm': 302.0,
        'width_mm': 172.0,
        'height_mm': 220.0,
        'size_type': 'JIS D31',
        'terminal_type': 'стандарт',
        'polarity': 'обратная (0, L)',
        'serviceable': 'да',
        'weight': 24.0,
        'bottom_mount': 'B01',
        'warranty_months': 12.0,
        'efb': 'да',
        'agm': 'нет',
        'price_group': '4 Премиум (цг)',
        'price_opt': 10340.0,
        'price_recommended': 14500.0,
        'rest_count': '>30',
    }


def test_actual_plant_fields_remain_typed_and_separate(plant_fields: dict[str, object]) -> None:
    original = plant_fields.copy()
    battery = BatteryItem.from_fields(plant_fields)

    assert_type(battery.product_group, Literal[ProductGroup.BATTERIES])
    assert battery.product_group is ProductGroup.BATTERIES
    assert battery.identity.code == '0123247'
    assert battery.identity.title == 'XTREME +EFB 100 обр (125D31L)'
    assert battery.electrical.capacity_ah == Decimal('100')
    assert battery.electrical.starting_current_a == Decimal('850')
    assert battery.electrical.efb is True
    assert battery.electrical.agm is False
    assert battery.case.length_mm == Decimal('302')
    assert battery.case.serviceable is True
    assert battery.offer.rest_count == 30
    assert battery.offer.sale_price == Decimal('14500')
    assert battery.offer.price_opt == Decimal('10340')
    assert plant_fields == original


def test_unknown_values_do_not_become_zero_or_false() -> None:
    battery = BatteryItem.from_fields({})

    assert battery == BatteryItem()
    assert battery.electrical.efb is None
    assert battery.electrical.agm is None
    assert battery.case.weight is None
    assert battery.offer.rest_count is None
    assert battery.offer.sale_price is None


def test_registry_describes_exactly_the_model_fields() -> None:
    groups = (BatteryIdentity, BatteryParameters, BatteryCase, BatteryOffer)
    model_fields = {attribute.name for group in groups for attribute in fields(group)}

    assert set(FIELD_KEYS) == model_fields
    assert len(FIELD_KEYS) == len(model_fields)
    assert 'capacity_ah' not in TIRE_FIELDS
    assert 'width' not in FIELD_KEYS
    with pytest.raises(TypeError):
        mutate: Callable[..., None] = setitem
        mutate(FIELD_CONVERTERS, 'width', str)


@pytest.mark.parametrize('key', ['width', 'diameter', 'disk_type', 'unexpected'])
def test_foreign_fields_are_rejected_with_name(key: str) -> None:
    with pytest.raises(ValueError, match=key):
        BatteryItem.from_fields({key: '16'})


@pytest.mark.parametrize('attribute', ['identity', 'electrical', 'case', 'offer', 'product_group'])
def test_item_cannot_change_after_creation(attribute: str) -> None:
    with pytest.raises((FrozenInstanceError, TypeError)):
        setattr(BatteryItem(), attribute, None)


_INVALID_NUMBERS = [False, True, [], {}, 'NaN', 'Infinity', float('inf'), 'не число']


@pytest.mark.parametrize('raw', _INVALID_NUMBERS)
def test_invalid_number_contains_field_path(raw: object) -> None:
    with pytest.raises(ValueError, match='capacity_ah'):
        BatteryItem.from_fields({'capacity_ah': raw})


@pytest.mark.parametrize('key', ['capacity_ah', 'starting_current_a', 'length_mm', 'width_mm', 'height_mm', 'weight'])
@pytest.mark.parametrize('raw', [0, -1])
def test_physical_values_must_be_positive(key: str, raw: int) -> None:
    with pytest.raises(ValueError, match=key):
        BatteryItem.from_fields({key: raw})


@pytest.mark.parametrize('key', ['price_opt', 'price_recommended', 'rest_count', 'warranty_months'])
def test_negative_commercial_values_are_rejected(key: str) -> None:
    with pytest.raises(ValueError, match=key):
        BatteryItem.from_fields({key: -1})


@pytest.mark.parametrize('key', ['rest_count', 'warranty_months'])
@pytest.mark.parametrize('raw', [True, False, '1.5'])
def test_integer_values_do_not_round_or_accept_boolean(key: str, raw: object) -> None:
    with pytest.raises(ValueError, match=key):
        BatteryItem.from_fields({key: raw})


@pytest.mark.parametrize('raw', ['>30', '> 30', 'более 30', '<30', 30, 30.0])
def test_stock_matches_tire_normalization(raw: object) -> None:
    assert BatteryItem.from_fields({'rest_count': raw}).offer.rest_count == 30


def test_one_item_and_zero_are_distinct_valid_stocks() -> None:
    assert BatteryItem.from_fields({'rest_count': 1}).offer.rest_count == 1
    assert BatteryItem.from_fields({'rest_count': 0}).offer.rest_count == 0


@pytest.mark.parametrize('key', ['efb', 'agm', 'serviceable'])
@pytest.mark.parametrize(
    'raw, expected',
    [
        pytest.param('да', True),
        pytest.param(' ДА ', True),
        pytest.param('нет', False),
        pytest.param(False, False),
        pytest.param(True, True),
    ],
)
def test_flags_preserve_the_meaning_of_no(key: str, raw: object, expected: bool) -> None:
    battery = BatteryItem.from_fields({key: raw})
    characteristics = {**asdict(battery.electrical), **asdict(battery.case)}
    assert characteristics[key] is expected


@pytest.mark.parametrize('raw', [0, 1, '0', '1', 'возможно', []])
def test_ambiguous_flags_are_rejected(raw: object) -> None:
    with pytest.raises(ValueError, match='agm'):
        BatteryItem.from_fields({'agm': raw})


@pytest.mark.parametrize('raw', [None, '', '  '])
def test_empty_cells_preserve_unknown(raw: object) -> None:
    battery = BatteryItem.from_fields(dict.fromkeys(FIELD_KEYS, raw))
    assert battery == BatteryItem()


@pytest.mark.parametrize(
    'raw, expected',
    [
        pytest.param(600402083.0, '600402083'),
        pytest.param('0123247   ', '0123247'),
        pytest.param(12, '12'),
    ],
)
def test_codes_preserve_textual_zeroes_and_remove_excel_fraction(raw: object, expected: str) -> None:
    assert BatteryItem.from_fields({'code': raw}).identity.code == expected


@pytest.mark.parametrize('raw', [False, True, [], {}])
def test_invalid_text_cells_are_rejected(raw: object) -> None:
    with pytest.raises(ValueError, match='code'):
        BatteryItem.from_fields({'code': raw})


def test_decimal_values_keep_precision_and_zero_prices() -> None:
    battery = BatteryItem.from_fields({'price_opt': '1 234,56', 'price_recommended': Decimal('0')})
    assert battery.offer.price_opt == Decimal('1234.56')
    assert battery.offer.sale_price == Decimal('0')
    assert BatteryItem.from_fields({'code': 12.5}).identity.code == '12.5'


def test_missing_recommended_price_never_falls_back_to_purchase() -> None:
    assert BatteryItem.from_fields({'price_opt': 100}).offer.sale_price is None


@pytest.mark.parametrize(
    'constructor, kwargs, key',
    [
        (BatteryParameters, {'capacity_ah': Decimal('-1')}, 'capacity_ah'),
        (BatteryParameters, {'starting_current_a': Decimal('NaN')}, 'starting_current_a'),
        (BatteryCase, {'length_mm': 10}, 'length_mm'),
        (BatteryOffer, {'rest_count': True}, 'rest_count'),
        (BatteryOffer, {'warranty_months': -1}, 'warranty_months'),
        (BatteryParameters, {'efb': 'нет'}, 'efb'),
        (BatteryParameters, {'agm': 0}, 'agm'),
        (BatteryCase, {'serviceable': 'да'}, 'serviceable'),
    ],
)
def test_direct_construction_cannot_bypass_invariants(
    constructor: Callable[..., object],
    kwargs: dict[str, object],
    key: str,
) -> None:
    with pytest.raises(ValueError, match=key):
        constructor(**kwargs)


def test_registry_conversions_agree_with_typed_model(plant_fields: dict[str, object]) -> None:
    """Каждый ключ реестра соответствует преобразованию своего типизированного поля."""
    plant_fields.update(
        {
            'current_standard': 'EN',
            'supplier_name': 'План-Т',
            'certificate_url': 'https://example.org/certificate',
        }
    )
    battery = BatteryItem.from_fields(plant_fields)
    actual = {}
    for component in (battery.identity, battery.electrical, battery.case, battery.offer):
        actual.update(asdict(component))
    expected = {}
    for key, converter in FIELD_CONVERTERS.items():
        raw = plant_fields.get(key)
        expected[key] = converter(raw)
    assert actual == expected
