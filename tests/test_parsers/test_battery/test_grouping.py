"""Правила дублей аккумуляторов и сохранения предложений поставщиков."""

from dataclasses import replace
from itertools import permutations

import pytest

from domain.battery.duplicate import BatteryDuplicate
from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from parsers.battery.group_keys import identity_key
from parsers.battery.grouping import group_batteries
from parsers.battery.handler import BatteryHandler
from parsers.battery.offer_repeats import unique_offers
from parsers.vendor_config.battery_settings import BatterySettings


def _position(**changes: object) -> BatteryItem:
    return BatteryItem.from_fields(
        {
            'manufacturer_name': 'Алькор (Тюмень)',
            'model': 'XTREME +EFB',
            'capacity_ah': 60,
            'starting_current_a': 650,
            'length_mm': 242,
            'width_mm': 175,
            'height_mm': 190,
            'terminal_type': 'стандарт',
            'polarity': '0, L',
            'efb': True,
            'agm': False,
            'supplier_name': 'plant',
            'code': '001',
            'code_art': 'article',
            'price_recommended': 8000,
            'rest_count': 10,
            **changes,
        }
    )


def _group_ids(package: BatteryResult) -> list[int]:
    return [position.duplicate.group_id for position in package.positions]


def test_different_articles_and_suppliers_keep_independent_offers() -> None:
    first = _position()
    second = _position(supplier_name='other', code='002', code_art='other', price_recommended=7000, rest_count=5)
    battery_handler = BatteryHandler(BatterySettings(), 'plant')
    grouped = battery_handler.group(BatteryResult((first, second)))
    assert _group_ids(grouped) == [1, 1]
    assert [position.duplicate.is_main for position in grouped.positions] == [False, True]
    assert [position.offer for position in grouped.positions] == [first.offer, second.offer]
    assert [position.identity for position in grouped.positions] == [first.identity, second.identity]
    assert first.duplicate.group_id == 0
    assert group_batteries(grouped) == grouped


@pytest.mark.parametrize(
    'changes',
    [
        {'manufacturer_name': 'Другой'},
        {'model': 'XTREME Arctic'},
        {'capacity_ah': 66},
        {'starting_current_a': 690},
        {'length_mm': 243},
        {'width_mm': 176},
        {'height_mm': 191},
        {'terminal_type': 'тонкие'},
        {'polarity': '1, R'},
        {'efb': False},
        {'agm': True},
    ],
)
def test_each_main_characteristic_prevents_merging(changes: dict[str, object]) -> None:
    second = _position(code='002', **changes)
    grouped = group_batteries(BatteryResult((_position(), second)))
    assert _group_ids(grouped) == [1, 2]


@pytest.mark.parametrize(
    'field_name',
    [
        'manufacturer_name',
        'model',
        'capacity_ah',
        'starting_current_a',
        'length_mm',
        'width_mm',
        'height_mm',
        'terminal_type',
        'polarity',
        'efb',
        'agm',
    ],
)
def test_incomplete_main_key_never_merges(field_name: str) -> None:
    missing = {field_name: None}
    positions = (_position(**missing), _position(code='002', **missing))
    assert _group_ids(group_batteries(BatteryResult(positions))) == [1, 2]


@pytest.mark.parametrize(
    'field_name, first_value, second_value',
    [
        ('size_type', 'DIN L2', 'DIN L3'),
        ('bottom_mount', 'B01', 'B13'),
        ('serviceable', False, True),
        ('current_standard', 'EN', 'SAE'),
    ],
)
def test_optional_unknown_joins_only_unique_known_variant(
    field_name: str,
    first_value: object,
    second_value: object,
) -> None:
    unknown = _position()
    first = _position(code='002', **{field_name: first_value})
    second = _position(code='003', **{field_name: second_value})
    assert _group_ids(group_batteries(BatteryResult((unknown, first)))) == [1, 1]
    for positions in permutations((unknown, first, second)):
        grouped = group_batteries(BatteryResult(positions))
        assert len(set(_group_ids(grouped))) == 3


def test_optional_unknown_does_not_bridge_incompatible_combinations() -> None:
    positions = (
        _position(size_type='DIN L2'),
        _position(code='002', bottom_mount='B01'),
        _position(code='003', size_type='DIN L3', bottom_mount='B13'),
    )
    for ordered in permutations(positions):
        assert len(set(_group_ids(group_batteries(BatteryResult(ordered))))) == 3


def test_case_whitespace_and_decimal_representation_are_normalized() -> None:
    second = _position(
        code='002',
        manufacturer_name='  АЛЬКОР   (ТЮМЕНЬ) ',
        model=' xtreme  +efb ',
        capacity_ah='60.00',
        terminal_type=' СТАНДАРТ ',
        polarity=' 0,  L ',
    )
    grouped = group_batteries(BatteryResult((_position(), second)))
    assert _group_ids(grouped) == [1, 1]


def test_non_identity_characteristics_do_not_merge_or_disappear() -> None:
    second = _position(
        code='002',
        title='другое название',
        weight=20,
        warranty_months=36,
        price_opt=100,
        price_group='другая',
        certificate_url='https://example.org',
    )
    grouped = group_batteries(BatteryResult((_position(), second)))
    assert _group_ids(grouped) == [1, 1]
    assert grouped.positions[1].case == second.case
    assert grouped.positions[1].offer == second.offer


@pytest.mark.parametrize(
    'prices, main_index',
    [
        ((8000, 8000), 0),
        ((8000, 0), 1),
        ((None, 8000), 1),
        ((None, None), 0),
    ],
)
def test_main_offer_uses_price_then_original_order(prices: tuple[int | None, int | None], main_index: int) -> None:
    first = _position(price_recommended=prices[0])
    second = _position(code='002', price_recommended=prices[1])
    positions = (first, second)
    grouped = group_batteries(BatteryResult(positions))
    assert grouped.positions[main_index].duplicate.is_main
    assert sum(position.duplicate.is_main for position in grouped.positions) == 1


def test_identical_offer_repeat_is_counted_once() -> None:
    first = _position()
    repeated = replace(first)
    grouped = group_batteries(BatteryResult((first, repeated)))
    assert len(grouped.positions) == 1
    assert grouped.positions[0].offer.rest_count == 10


@pytest.mark.parametrize(
    'changes',
    [
        {'rest_count': 5},
        {'price_recommended': 7000},
        {'capacity_ah': 66},
    ],
)
def test_conflicting_offer_address_is_reported(changes: dict[str, object]) -> None:
    with pytest.raises(ValueError, match=r'\[batteries\] plant, код 001: конфликт'):
        group_batteries(BatteryResult((_position(), _position(**changes))))


@pytest.mark.parametrize('missing', ['code', 'supplier_name'])
def test_unknown_offer_address_is_not_deduplicated(missing: str) -> None:
    position = _position(**{missing: None})
    grouped = group_batteries(BatteryResult((position, position)))
    assert len(grouped.positions) == 2
    assert _group_ids(grouped) == [1, 1]


def test_empty_package_retains_batteries() -> None:
    assert group_batteries(BatteryResult()) == BatteryResult()


def test_blank_main_string_prevents_merging() -> None:
    positions = (_position(model=' '), _position(code='002', model=''))
    assert _group_ids(group_batteries(BatteryResult(positions))) == [1, 2]


def test_regrouping_replaces_previous_duplicate_marks() -> None:
    first = replace(_position(), duplicate=BatteryDuplicate(91, True))
    second = replace(_position(code='002'), duplicate=BatteryDuplicate(92, True))

    grouped = group_batteries(BatteryResult((first, second)))

    assert _group_ids(grouped) == [1, 1]
    assert [position.duplicate.is_main for position in grouped.positions] == [True, False]


def test_unique_offers_clears_previous_duplicate_marks() -> None:
    marked = replace(_position(), duplicate=BatteryDuplicate(91, True))

    assert unique_offers((marked,))[0].duplicate == BatteryDuplicate()


def test_identity_key_uses_single_spaces() -> None:
    single = _position()
    spaced = _position(
        code='002',
        manufacturer_name='  АЛЬКОР   (ТЮМЕНЬ) ',
        model=' xtreme  +efb ',
        polarity=' 0,  L ',
    )

    assert identity_key(spaced) == identity_key(single)
    assert identity_key(spaced)[0] == 'алькор (тюмень)'
