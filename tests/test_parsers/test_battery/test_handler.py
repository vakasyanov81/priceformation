"""Контракты обработки аккумуляторов: линейки, публикация и независимость цен."""

from dataclasses import replace
from decimal import Decimal

import pytest

from cfg.battery import make_battery_handler
from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from domain.product_group_handler import ProductGroupHandler
from domain.product_groups import ProductGroup
from parsers.battery.handler import BatteryHandler
from parsers.battery.title import normalize_title
from parsers.vendor_config.battery_settings import BatterySettings
from parsers.vendor_config.group_models import BatterySection


def _battery_handler() -> BatteryHandler:
    section = BatterySection(
        'plant',
        'План-Т',
        6,
        ('*.xls',),
        columns={1: 'title', 2: 'rest_count', 21: 'code', 24: 'price_recommended'},
        processing=BatterySettings.from_dict(
            {'pricing': {'rules': {'markup_rules': [{'min': 0, 'max': 999999999, 'percent': 0.2}]}}},
            'plant.json',
        ),
    )
    return make_battery_handler(section, 'plant')


def _fields(**changes: object) -> dict[str, object]:
    return {
        'code': '001',
        'title': '  XTREME   +EFB 60 обр (L2.0) ',
        'rest_count': '>30',
        'price_opt': '4000.10',
        'price_recommended': '5000.20',
        **changes,
    }


def test_handler_keeps_price_stock_and_unknown_characteristics() -> None:
    battery_handler: ProductGroupHandler[BatteryItem] = _battery_handler()
    position = battery_handler.create_position(_fields())
    parsed = battery_handler.process([position])
    actual = parsed.positions[0]

    assert battery_handler.product_group is ProductGroup.BATTERIES
    assert actual.identity.title == 'XTREME +EFB 60 обр (L2.0)'
    assert actual.identity.model == 'XTREME +EFB'
    assert actual.identity.code == '001'
    assert actual.offer.supplier_name == 'plant'
    assert actual.offer.sale_price == Decimal('5000.20')
    assert actual.offer.price_opt == Decimal('4000.10')
    assert actual.offer.rest_count == 30
    assert actual.electrical.capacity_ah is None
    assert actual.electrical.efb is None
    assert position.identity.model is None


@pytest.mark.parametrize('stock', [1, 2, 3, 4])
def test_single_battery_can_be_published(stock: int) -> None:
    battery_handler = _battery_handler()
    position = battery_handler.create_position(_fields(rest_count=stock, price_opt=None))
    parsed = battery_handler.process([position])
    assert parsed.positions[0].offer.sale_price == Decimal('5000.20')


@pytest.mark.parametrize(
    'purchase, recommended, expected',
    [
        ('5000', '5000', '6000'),
        ('4000.10', '4000.10', '4800.12'),
        ('5000', '5000.01', '5000.01'),
        ('5000', '4999.99', '6000'),
        ('5000', '4900', '6000'),
        (None, '5000', '5000'),
        ('0', '0', '0'),
    ],
)
def test_nonprofitable_prices_receive_markup(purchase: str | None, recommended: str, expected: str) -> None:
    battery_handler = _battery_handler()
    position = battery_handler.create_position(_fields(price_opt=purchase, price_recommended=recommended))
    parsed = battery_handler.process([position])
    actual = parsed.positions[0]

    assert actual.offer.sale_price == Decimal(expected)
    assert actual.offer.price_opt == position.offer.price_opt
    assert actual.offer.price_recommended == Decimal(recommended)
    assert position.offer.sale_price == Decimal(recommended)
    assert battery_handler.prepare_output(parsed)[0]['sale_price'] == expected
    repeated = battery_handler.process(parsed.positions)
    assert repeated.positions[0].offer.sale_price == Decimal(expected)


@pytest.mark.parametrize(
    'changes, issue',
    [
        ({'code': None}, 'code'),
        ({'title': ' '}, 'title'),
        ({'price_recommended': None}, 'price_recommended'),
        ({'rest_count': 0}, 'остаток 0'),
        ({'rest_count': None}, 'остаток None'),
        ({'rest_count': '?'}, 'остаток None'),
    ],
)
def test_unpublishable_offer_is_excluded_with_context(
    changes: dict[str, object],
    issue: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    battery_handler = _battery_handler()
    parsed = battery_handler.process([battery_handler.create_position(_fields(**changes))])
    assert parsed == BatteryResult()
    assert '[batteries] plant, код' in caplog.text
    assert issue in caplog.text


@pytest.mark.parametrize(
    'title', ['XTREME Classic 132 пр (A.4, конус, AL)', 'Неизвестная линейка 60', 'prefix XTREME Arctic 60']
)
def test_unknown_line_preserves_title_without_inventing_model(title: str) -> None:
    battery_handler = _battery_handler()
    parsed = battery_handler.process_fields([_fields(title=title)])
    assert parsed.positions[0].identity.title == title
    assert parsed.positions[0].identity.model is None


@pytest.mark.parametrize('raw_title, expected', [('  Новая   серия  60  ', 'Новая серия 60'), (None, '')])
def test_normalize_title_handles_direct_unknown_titles(raw_title: str | None, expected: str) -> None:
    position = _battery_handler().create_position(_fields())
    position = replace(position, identity=replace(position.identity, title=raw_title))

    actual = normalize_title(position, ('XTREME +EFB',))

    assert actual.identity.title == expected
    assert actual.identity.model is None


def test_normalize_title_normalizes_matched_title_without_declared_model() -> None:
    position = _battery_handler().create_position(_fields(model=None))
    position = replace(position, identity=replace(position.identity, title='  xtreme   +EFB  60  '))

    actual = normalize_title(position, ('XTREME +EFB',))

    assert actual.identity.title == 'xtreme +EFB 60'
    assert actual.identity.model == 'XTREME +EFB'


def test_line_matching_normalizes_case_and_spaces_without_removing_words() -> None:
    battery_handler = _battery_handler()
    position = battery_handler.create_position(_fields(title='  xtreme  ARCTIC 100 обр ', model='xtreme Arctic'))
    actual = battery_handler.process([position]).positions[0]
    assert actual.identity.model == 'XTREME Arctic'
    assert actual.identity.title == 'xtreme ARCTIC 100 обр'


def test_conflicting_line_is_rejected() -> None:
    battery_handler = _battery_handler()
    with pytest.raises(ValueError, match='не совпадает'):
        battery_handler.process([battery_handler.create_position(_fields(model='XTREME Arctic'))])


def test_ambiguous_line_list_is_rejected_during_processing() -> None:
    battery_handler = BatteryHandler(BatterySettings(lines=('XTREME', 'XTREME +EFB')), 'plant')
    with pytest.raises(ValueError, match='ожидается одна'):
        battery_handler.process([battery_handler.create_position(_fields())])


def test_explicit_line_can_match_complete_title() -> None:
    battery_handler = _battery_handler()
    parsed = battery_handler.process([battery_handler.create_position(_fields(title='XTREME Arctic'))])
    assert parsed.positions[0].identity.model == 'XTREME Arctic'


def test_empty_package_preserves_group_through_output() -> None:
    battery_handler = _battery_handler()
    assert battery_handler.process([]) == BatteryResult()
    assert battery_handler.group(BatteryResult()) == BatteryResult()
    assert battery_handler.prepare_output(BatteryResult()) == ()


def test_section_headers_are_excluded_before_model_creation() -> None:
    battery_handler = _battery_handler()
    parsed = battery_handler.process_fields(
        [
            {'title': 'Раздел аккумуляторов', 'capacity_ah': 'не число'},
            _fields(),
            {'code': '  ', 'price_recommended': 'РРЦ'},
        ]
    )
    assert len(parsed.positions) == 1
    assert parsed.positions[0].identity.code == '001'


def test_creation_error_preserves_field_and_supplier_context() -> None:
    battery_handler = _battery_handler()
    with pytest.raises(ValueError, match=r'\[batteries\] plant, код 001: capacity_ah') as caught:
        battery_handler.process_fields([_fields(capacity_ah=-1)])
    assert isinstance(caught.value.__cause__, ValueError)


def test_zero_recommended_price_receives_markup_on_purchase() -> None:
    battery_handler = _battery_handler()
    parsed = battery_handler.process_fields([_fields(price_recommended=0)])
    assert parsed.positions[0].offer.sale_price == Decimal('4800.12')
    assert parsed.positions[0].offer.price_recommended == Decimal(0)
    assert parsed.positions[0].offer.price_opt == Decimal('4000.10')


@pytest.mark.parametrize(
    'raw, expected',
    [
        ('*12', 12),
        (' *12 ', 12),
        ('ъъъ0,5', None),
    ],
)
def test_plant_warranty_is_normalized_before_model_creation(raw: str, expected: int | None) -> None:
    fields = _fields(warranty_months=raw)
    original = fields.copy()
    position = _battery_handler().create_position(fields)
    assert position.offer.warranty_months == expected
    assert fields == original


def test_unlisted_declared_model_is_preserved() -> None:
    parsed = _battery_handler().process_fields([_fields(title='Новая серия 60', model='Новая серия')])
    assert parsed.positions[0].identity.model == 'Новая серия'


def test_unpublishable_offer_does_not_stop_following_positions() -> None:
    battery_handler = _battery_handler()
    skipped = battery_handler.create_position(_fields(code='skipped', rest_count=0))
    published = battery_handler.create_position(_fields(code='published'))

    parsed = battery_handler.process([skipped, published])

    assert [position.identity.code for position in parsed.positions] == ['published']


def test_line_conflict_error_contains_offer_code() -> None:
    battery_handler = _battery_handler()
    position = battery_handler.create_position(_fields(code='A-17', model='XTREME Arctic'))

    with pytest.raises(ValueError) as caught:
        battery_handler.process([position])

    assert str(caught.value).startswith('[batteries] plant, код A-17: ')


def test_all_missing_required_fields_are_listed_in_order(caplog: pytest.LogCaptureFixture) -> None:
    battery_handler = _battery_handler()
    position = battery_handler.create_position(_fields(code=None, title=None, price_recommended=None))

    assert battery_handler.process([position]) == BatteryResult()

    assert 'отсутствуют обязательные поля: code, title, price_recommended' in caplog.text


def test_unknown_line_title_is_normalized() -> None:
    parsed = _battery_handler().process_fields([_fields(title='  Новая   серия  60  ')])

    assert parsed.positions[0].identity.title == 'Новая серия 60'
    assert parsed.positions[0].identity.model is None


def test_markup_uses_rule_matching_purchase_instead_of_default() -> None:
    settings = BatterySettings.from_dict(
        {
            'pricing': {
                'rules': {
                    'markup_rules': [
                        {'min': 0, 'max': 100, 'percent': 0.2},
                        {'min': 101, 'max': 1000, 'percent': 0.5},
                    ]
                }
            }
        },
        'plant.json',
    )
    battery_handler = BatteryHandler(settings, 'plant')
    position = battery_handler.create_position(_fields(price_opt=200, price_recommended=200))

    parsed = battery_handler.process([position])

    assert parsed.positions[0].offer.sale_price == Decimal(300)
