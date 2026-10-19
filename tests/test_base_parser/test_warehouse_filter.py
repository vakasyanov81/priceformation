"""CityWarehouseFilter: остаток только на складах выбранных городов."""

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
    (1, 10),
    (2, 10),
    (5, 10),
    (3, 0),
    (4, 0),
    (6, 0),
    (777, 0),
    (None, 0),
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


def _rest_after(warehouse_id: int | None, cities: tuple[str, ...] = ('Новосибирск',)) -> int:
    row = RowItem({'rest_count': 10, 'warehouse_id': warehouse_id})
    CityWarehouseFilter(folder=_FOLDER, cities=cities).apply(row)
    return row.stock.rest_count or 0


@pytest.mark.parametrize(
    ('warehouse_id', 'expected_rest'),
    _CASES,
)
def test_keeps_rest_only_in_city_warehouses(
    fake_config_provider: FakeConfigProvider,
    warehouse_id: int | None,
    expected_rest: int,
) -> None:
    """Склад города (по названию или адресу, без учёта регистра) оставляет остаток, остальные и без ID — обнуляют."""
    _write_territories(fake_config_provider, _TERRITORIES)

    assert _rest_after(warehouse_id) == expected_rest


def test_several_cities(fake_config_provider: FakeConfigProvider) -> None:
    _write_territories(fake_config_provider, _TERRITORIES)

    assert _rest_after(6, cities=('Новосибирск', 'Тюмень')) == 10


def test_territories_are_read_once(fake_config_provider: FakeConfigProvider) -> None:
    path = _write_territories(fake_config_provider, _TERRITORIES)
    city_filter = CityWarehouseFilter(folder=_FOLDER, cities=('Новосибирск',))
    city_filter.apply(RowItem({'rest_count': 1, 'warehouse_id': 1}))

    path.unlink()
    row = RowItem({'rest_count': 10, 'warehouse_id': 2})
    city_filter.apply(row)

    assert row.stock.rest_count == 10


def test_missing_file_is_error(fake_config_provider: FakeConfigProvider) -> None:
    with (
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(WarehouseFilterError, match='Не найден список складов'),
    ):
        _rest_after(1)


@pytest.mark.parametrize(
    'payload', ['не json', '{"id": 1}', '[{"id": "1"}]', '[{"id": "x", "name": "a", "address": "b"}]']
)
def test_broken_file_is_error(fake_config_provider: FakeConfigProvider, payload: str) -> None:
    _write_territories(fake_config_provider, payload)

    with (
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(WarehouseFilterError, match='не разобран'),
    ):
        _rest_after(1)


def test_no_matching_city_is_error(fake_config_provider: FakeConfigProvider) -> None:
    """Город, которого нет в списке, — ошибка настройки, а не молча пустой прайс."""
    _write_territories(fake_config_provider, _TERRITORIES)

    with (
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(WarehouseFilterError, match='Атлантида'),
    ):
        _rest_after(1, cities=('Атлантида',))


def test_base_parser_pipeline_applies_filter(fake_config_provider: FakeConfigProvider) -> None:
    """Хук парсера обнуляет остаток склада вне города до шагов pipeline."""
    from parsers.base_parser.base_parser import BaseParser
    from parsers.base_parser.strategy_hooks import StrategyHooks

    _write_territories(fake_config_provider, _TERRITORIES)
    hooks = StrategyHooks(warehouse_filter=CityWarehouseFilter(folder=_FOLDER, cities=('Новосибирск',)))
    outside = RowItem({'rest_count': 10, 'warehouse_id': 6})
    inside = RowItem({'rest_count': 10, 'warehouse_id': 1})

    BaseParser.apply_warehouse_filter(hooks, outside)
    BaseParser.apply_warehouse_filter(hooks, inside)
    BaseParser.apply_warehouse_filter(StrategyHooks(), RowItem({'rest_count': 10, 'warehouse_id': 6}))

    assert (outside.stock.rest_count, inside.stock.rest_count) == (0, 10)


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
