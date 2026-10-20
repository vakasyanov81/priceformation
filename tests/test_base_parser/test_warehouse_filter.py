"""CityWarehouseFilter: позиции только со складов выбранных городов."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from domain.exceptions import CoreExceptionError
from domain.row_item.row_item import RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser.warehouse_filter import CityWarehouseFilter, WarehouseFilterError

_FOLDER = 'mim'
_TO_LOG = 'to_log'
_CASES = [
    (1, True),
    (2, True),
    (5, True),
    (3, False),
    (4, False),
    (6, False),
    (777, False),
    (None, False),
]
_TERRITORIES: list[dict[str, Any]] = [
    {'name': 'ЦС Новосибирск', 'type': 'storage', 'id': '1', 'address': 'Новосибирская обл., Двуречье п.'},
    {'name': 'ПВ Новосибирск Кирова', 'type': 'shop', 'id': '2', 'address': '630063, город Новосибирск'},
    {'name': 'СП Бердск', 'type': 'partner', 'id': '3', 'address': 'Новосибирская обл., Бердск г.'},
    {'name': 'ПВ Красноярск Новосибирская', 'type': 'shop', 'id': '4', 'address': 'Красноярск, улица Новосибирская'},
    {'name': 'НС.Под заказ', 'type': 'for_order', 'id': '5', 'address': 'новосибирск. Под заказ'},
    {'name': 'ЦС Тюмень', 'type': 'storage', 'id': '6', 'address': 'Тюмень'},
]


def _write_territories(provider: FakeConfigProvider, payload: Any) -> Path:
    folder = Path(provider.price_folder(_FOLDER))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'territories.json'
    text = payload if isinstance(payload, str) else json.dumps(payload)
    path.write_text(text, encoding='utf-8')
    return path


def _allowed(warehouse_id: int | None, cities: tuple[str, ...] = ('Новосибирск',)) -> bool:
    row = RowItem({'rest_count': 10, 'warehouse_id': warehouse_id})
    return CityWarehouseFilter(folder=_FOLDER, cities=cities).allows(row)


@pytest.mark.parametrize(
    ('warehouse_id', 'expected'),
    _CASES,
)
def test_allows_only_city_warehouses(
    fake_config_provider: FakeConfigProvider,
    warehouse_id: int | None,
    expected: bool,
) -> None:
    """Склад города (по названию или адресу, без учёта регистра) проходит, остальные и без ID — нет."""
    _write_territories(fake_config_provider, _TERRITORIES)

    assert _allowed(warehouse_id) is expected


def test_several_cities(fake_config_provider: FakeConfigProvider) -> None:
    _write_territories(fake_config_provider, _TERRITORIES)

    assert _allowed(6, cities=('Новосибирск', 'Тюмень'))


def test_territories_are_read_once(fake_config_provider: FakeConfigProvider) -> None:
    path = _write_territories(fake_config_provider, _TERRITORIES)
    city_filter = CityWarehouseFilter(folder=_FOLDER, cities=('Новосибирск',))
    city_filter.allows(RowItem({'rest_count': 1, 'warehouse_id': 1}))

    path.unlink()

    assert city_filter.allows(RowItem({'rest_count': 10, 'warehouse_id': 2}))


def test_missing_file_is_error(fake_config_provider: FakeConfigProvider) -> None:
    with (
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(WarehouseFilterError, match='Не найден список складов'),
    ):
        _allowed(1)


@pytest.mark.parametrize(
    'payload', ['не json', '{"id": 1}', '[{"id": "1"}]', '[{"id": "x", "name": "a", "address": "b"}]']
)
def test_broken_file_is_error(fake_config_provider: FakeConfigProvider, payload: str) -> None:
    _write_territories(fake_config_provider, payload)

    with (
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(WarehouseFilterError, match='не разобран'),
    ):
        _allowed(1)


def test_no_matching_city_is_error(fake_config_provider: FakeConfigProvider) -> None:
    """Город, которого нет в списке, — ошибка настройки, а не молча пустой прайс."""
    _write_territories(fake_config_provider, _TERRITORIES)

    with (
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(WarehouseFilterError, match='Атлантида'),
    ):
        _allowed(1, cities=('Атлантида',))


def test_base_parser_drops_foreign_warehouses_before_enrich(fake_config_provider: FakeConfigProvider) -> None:
    """Позиции складов вне города отсеиваются целиком, а не получают нулевой остаток."""
    from parsers.base_parser.base_parser import BaseParser
    from parsers.base_parser.strategy_hooks import StrategyHooks

    _write_territories(fake_config_provider, _TERRITORIES)
    hooks = StrategyHooks(warehouse_filter=CityWarehouseFilter(folder=_FOLDER, cities=('Новосибирск',)))
    warehouse_ids = (6, 1, None, 2)
    rows = [RowItem({'rest_count': 10, 'warehouse_id': wid}) for wid in warehouse_ids]
    parser = BaseParser.__new__(BaseParser)
    parser._strategy_hooks = hooks  # noqa: WPS437
    plain = BaseParser.__new__(BaseParser)
    plain._strategy_hooks = StrategyHooks()  # noqa: WPS437

    kept = parser.filter_warehouses(rows)

    assert [row.stock.warehouse_id for row in kept] == [1, 2]
    assert plain.filter_warehouses(rows) == rows
    assert all(row.stock.rest_count == 10 for row in kept)


def test_base_parser_applies_order_from_warehouse_name() -> None:
    """Флаг order_from_warehouse_name включает разбор названия склада."""
    from parsers.base_parser.base_parser import BaseParser
    from parsers.base_parser.strategy_hooks import StrategyHooks

    enabled = RowItem({'warehouse_name': 'НС.Под заказ от 4д.'})
    disabled = RowItem({'warehouse_name': 'НС.Под заказ'})

    BaseParser.apply_warehouse_order(StrategyHooks(order_from_warehouse_name=True), enabled)
    BaseParser.apply_warehouse_order(StrategyHooks(), disabled)

    assert (enabled.stock.available, enabled.stock.delivery_period) == ('Под заказ', 4)
    assert disabled.stock.available is None
