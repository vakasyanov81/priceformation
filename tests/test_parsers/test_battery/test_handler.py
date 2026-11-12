"""Контракты обработки аккумуляторов: линейки, публикация и независимость цен."""

from decimal import Decimal

import pytest

from cfg.battery import make_battery_handler
from domain.battery.item import BatteryItem
from domain.battery.result import BatteryResult
from domain.product_group_handler import ProductGroupHandler
from domain.product_groups import ProductGroup
from parsers.battery.handler import BatteryHandler
from parsers.vendor_config.battery_settings import BatterySettings
from parsers.vendor_config.group_models import BatterySection


def _battery_handler() -> BatteryHandler:
    section = BatterySection(
        'plant',
        'План-Т',
        6,
        ('*.xls',),
        columns={1: 'title', 2: 'rest_count', 21: 'code', 24: 'price_recommended'},
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
    'changes, issue',
    [
        ({'code': None}, 'code'),
        ({'title': ' '}, 'title'),
        ({'price_recommended': None}, 'price_recommended'),
        ({'rest_count': 0}, 'остаток 0'),
        ({'rest_count': None}, 'остаток None'),
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


@pytest.mark.parametrize('title', ['XTREME +EFBX 60', 'Неизвестная линейка 60', 'prefix XTREME Arctic 60'])
def test_unknown_line_is_an_error_with_offer_context(title: str) -> None:
    battery_handler = _battery_handler()
    with pytest.raises(ValueError, match=r'\[batteries\] plant, код 001:.*линейка'):
        battery_handler.process([battery_handler.create_position(_fields(title=title))])


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


def test_grouping_and_output_are_not_silently_replaced() -> None:
    battery_handler = _battery_handler()
    assert battery_handler.process([]) == BatteryResult()
    with pytest.raises(NotImplementedError, match=r'8\.4'):
        battery_handler.group(BatteryResult())
    with pytest.raises(NotImplementedError, match=r'8\.5'):
        battery_handler.prepare_output(BatteryResult())


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


def test_zero_recommended_price_is_known_and_never_replaced_by_purchase_price() -> None:
    battery_handler = _battery_handler()
    parsed = battery_handler.process_fields([_fields(price_recommended=0)])
    assert parsed.positions[0].offer.sale_price == Decimal(0)
    assert parsed.positions[0].offer.price_opt == Decimal('4000.10')
