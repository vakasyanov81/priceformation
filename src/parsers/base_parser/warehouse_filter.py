"""Фильтр складов поставщика по городу: остаток вне выбранных городов обнуляется."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from domain.config_context import get_config_provider
from domain.exceptions import CoreExceptionError
from domain.row_item.row_item import RowItem

TERRITORIES_FILENAME = 'territories.json'
_MSG_NO_FILE = (
    'Не найден список складов {path}. Выгрузите данные поставщика по API, чтобы отфильтровать склады по городу.'
)
_MSG_BAD_FILE = 'Список складов {path} не разобран: ожидается JSON-массив территорий с полями id, name, address.'
_MSG_NO_MATCH = 'В списке складов {path} нет складов для городов: {cities}. Проверьте warehouse_cities в настройках.'


class WarehouseFilterError(CoreExceptionError):
    """Список складов поставщика отсутствует, повреждён или не содержит нужных городов."""


class CityWarehouseFilter:
    """Оставляет остаток только на складах выбранных городов.

    Склад ищется по `warehouse_id` позиции в списке территорий поставщика
    `file_prices/<folder>/territories.json`: город — слово целиком в названии или адресе
    территории (без учёта регистра), так «Новосибирск» не совпадёт с улицей «Новосибирская».
    Список читается при первой позиции, а не при сборке парсера: до первой выгрузки файла ещё нет.
    """

    def __init__(self, *, folder: str, cities: tuple[str, ...]) -> None:
        self._folder = folder
        self._cities = cities
        self._allowed_ids: frozenset[int] | None = None

    def apply(self, row_item: RowItem) -> None:
        """Обнулить остаток позиции, если её склад не из выбранных городов."""
        if row_item.stock.warehouse_id not in self._ids():
            row_item.set_field('rest_count', 0)

    def _ids(self) -> frozenset[int]:
        if self._allowed_ids is None:
            self._allowed_ids = self._load_ids()
        return self._allowed_ids

    def _load_ids(self) -> frozenset[int]:
        path = Path(get_config_provider().price_folder(self._folder)) / TERRITORIES_FILENAME
        if not path.is_file():
            raise WarehouseFilterError(_MSG_NO_FILE.format(path=path))
        matchers = [_city_pattern(city) for city in self._cities]
        allowed = frozenset(
            int(territory['id']) for territory in _read_territories(path) if _in_cities(territory, matchers)
        )
        if not allowed:
            raise WarehouseFilterError(_MSG_NO_MATCH.format(path=path, cities=', '.join(self._cities)))
        return allowed


def _city_pattern(city: str) -> re.Pattern[str]:
    """Город как слово целиком: «Новосибирск» не совпадёт с «Новосибирская»."""
    return re.compile(rf'(?<!\w){re.escape(city)}(?!\w)', re.IGNORECASE)


def _in_cities(territory: dict[str, Any], matchers: list[re.Pattern[str]]) -> bool:
    place = f'{territory["name"]} {territory["address"]}'
    return any(matcher.search(place) for matcher in matchers)


def _read_territories(path: Path) -> list[dict[str, Any]]:
    try:
        return [_normalized(territory) for territory in json.loads(path.read_text(encoding='utf-8'))]
    except (ValueError, KeyError, TypeError) as exc:
        raise WarehouseFilterError(_MSG_BAD_FILE.format(path=path)) from exc


def _normalized(territory: dict[str, Any]) -> dict[str, Any]:
    name = str(territory['name'])
    address = str(territory['address'])
    return {'id': int(territory['id']), 'name': name, 'address': address}
