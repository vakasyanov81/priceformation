"""
Стратегии слота `category`: назначают `type_production` строки.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from domain.row_item.row_item import RowItem
from parsers.base_parser.category_finder import canonical_product_type, raw_category_label
from parsers.strategies.product_types import CAMERA, DISK, GENERIC_TIRE, LIGHT_TRUCK, OTHER, PASSENGER, RIM_TAPE
from parsers.strategies.protocols import CategoryContext
from parsers.strategies.tire_category import non_tire_product_type
from parsers.vendor_config.slot_configs import CategoryConfig

_CATEGORY_FIELD = 'type_production'
_MANUFACTURER_CHUNK_INDEX = 1
_MANUFACTURER_HEAD_PREFIX = 'автошин'
# Суффикс легкогрузовой шины в диаметре: `15C`, `16LT` (латиница или кириллическая `С`).
_LIGHT_TRUCK_DIAMETER = re.compile(r'(?i)\d(?:c|с|lt)$')

# Канонизация первого слова строки-заголовка (падеж/число/регистр) к типу товара.
_HEADER_CATEGORIES: Mapping[str, str] = {
    'автошина': GENERIC_TIRE,
    'автошины': GENERIC_TIRE,
    'автокамера': CAMERA,
    'автокамеры': CAMERA,
    'диск': DISK,
    'диски': DISK,
    'ободная': RIM_TAPE,
    'прочие': OTHER,
}


class NoCategory:
    """Не менять категорию, пришедшую из прайса."""

    @classmethod
    def from_config(cls, config: CategoryConfig) -> NoCategory:
        """Стратегия без параметров."""
        return cls()

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
        """Категория не назначается."""


class FixedCategory:
    """Одна категория для всех строк секции."""

    def __init__(self, fixed_value: str) -> None:
        """Запомнить значение категории."""
        self._fixed_value = fixed_value

    @classmethod
    def from_config(cls, config: CategoryConfig) -> FixedCategory:
        """Взять категорию из поля `value`."""
        return cls(config.fixed_value)

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
        """Вернуть категорию секции."""
        return self._fixed_value


class TitleKeywordsCategory:
    """Категория по вхождению ключевых слов в заголовок (порядок ключей важен)."""

    def __init__(self, mapping: Mapping[str, str], default: str) -> None:
        """Запомнить упорядоченную карту ключей и значение по умолчанию."""
        self._mapping = mapping
        self._default = default

    @classmethod
    def from_config(cls, config: CategoryConfig) -> TitleKeywordsCategory:
        """Взять карту и default из конфига."""
        return cls(config.mapping, config.default_value)

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
        """Найти первый ключ в заголовке, иначе значение по умолчанию."""
        title = (row_item.identity.title or '').lower()
        for keyword, category in self._mapping.items():
            if keyword in title:
                return category
        return self._default


class FieldMapCategory:
    """Категория по значению поля строки через карту (регистр и пробелы нормализуются).

    С ``light_truck_by_diameter`` легковая шина с суффиксом C/LT в диаметре — легкогрузовая.
    """

    def __init__(
        self,
        field_name: str,
        mapping: Mapping[str, str],
        default: str,
        *,
        light_truck_by_diameter: bool = False,
    ) -> None:
        """Запомнить имя поля, карту значений, default и признак уточнения по диаметру."""
        self._field_name = field_name
        self._mapping = mapping
        self._default = default
        self._light_truck_by_diameter = light_truck_by_diameter

    @classmethod
    def from_config(cls, config: CategoryConfig) -> FieldMapCategory:
        """Взять поле и карту из конфига."""
        return cls(
            config.field_name,
            config.mapping,
            config.default_value,
            light_truck_by_diameter=config.light_truck_by_diameter,
        )

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
        """Сопоставить значение поля карте, иначе вернуть default."""
        raw_value = row_item.get_field(self._field_name)
        key = str(raw_value or '').lower().strip()
        category = self._mapping.get(key) or self._default
        if self._light_truck_by_diameter and category == PASSENGER and self._has_light_truck_suffix(row_item):
            return LIGHT_TRUCK
        return category

    def _has_light_truck_suffix(self, row_item: RowItem) -> bool:
        diameter = str(row_item.tire.diameter or '').strip()
        return _LIGHT_TRUCK_DIAMETER.search(diameter) is not None


class ColumnCanonicalCategory:
    """Канонизация категории из колонки; неизвестная — пустая строка."""

    def __init__(self, unknown_skip: bool) -> None:
        """Запомнить, нужно ли фиксировать неизвестные категории."""
        self._unknown_skip = unknown_skip

    @classmethod
    def from_config(cls, config: CategoryConfig) -> ColumnCanonicalCategory:
        """Взять флаг `unknown_skip` из конфига."""
        return cls(config.unknown_skip)

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
        """Канонизировать категорию; неизвестную — вернуть пустой строкой."""
        raw_type = row_item.get_field(_CATEGORY_FIELD)
        resolved = _canonical(raw_type, context)
        if resolved:
            return resolved
        if self._unknown_skip and context is not None:
            context.record_unknown_category(raw_category_label(raw_type))
        return ''


class HeaderRowsCategory:
    """Категория из строк-заголовков: состояние сохраняется между строками.

    Первый кусок заголовка канонизируется встроенной картой `_HEADER_CATEGORIES`
    (ключи в нижнем регистре), поверх неё ложится `map` из конфига;
    без совпадения возвращается `default`, иначе сырой кусок.

    Если заголовок перечисляет несколько видов товара через `/`
    (``Автокамеры/Ободная лента``), он неоднозначен: тип уточняется по названию
    строки (камера, лента, кольцо), а первый кусок остаётся запасным вариантом.
    """

    def __init__(
        self,
        zero_rest_categories: tuple[str, ...] = (),
        mapping: Mapping[str, str] | None = None,
        default: str = '',
    ) -> None:
        """Запомнить категории с нулевым остатком и карту канонизации."""
        self._zero_rest_categories = zero_rest_categories
        self._mapping = {**_HEADER_CATEGORIES, **(mapping or {})}
        self._default = default
        self.current_category = ''

    @classmethod
    def from_config(cls, config: CategoryConfig) -> HeaderRowsCategory:
        """Взять список категорий с нулевым остатком и карту из конфига."""
        return cls(config.zero_rest_categories, config.mapping, config.default_value)

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
        """Обновить раздел на строке-заголовке и вернуть тип товара строки."""
        header = self._header_title(row_item)
        if header is not None:
            self.current_category = header.lower().strip()
        if '/' in self.current_category:
            refined = non_tire_product_type(row_item.identity.title)
            if refined:
                return refined
        return self._first_chunk()

    def is_zero_rest_category(self) -> bool:
        """Относится ли текущий раздел к категориям с обнулённым остатком."""
        lowered = self.current_category.lower()
        return any(name in lowered for name in self._zero_rest_categories)

    def current_manufacturer(self) -> str | None:
        """Производитель из подписи текущего раздела: «автошины triangle» → «triangle»."""
        chunks = self.current_category.split()
        if len(chunks) <= _MANUFACTURER_CHUNK_INDEX or not chunks[0].startswith(_MANUFACTURER_HEAD_PREFIX):
            return None
        return chunks[_MANUFACTURER_CHUNK_INDEX]

    def _first_chunk(self) -> str:
        head = self.current_category.split('/')[0]
        chunk = head.split(' ')[0]
        return self._mapping.get(chunk, self._default or chunk)

    def _header_title(self, row_item: RowItem) -> str | None:
        """Название строки-заголовка раздела (есть title, нет цены); иначе None."""
        title = row_item.identity.title
        if title and not row_item.pricing.price_opt:
            return title
        return None


def _canonical(raw_type: str | None, context: CategoryContext | None) -> str | None:
    if context is None:
        return canonical_product_type(raw_type)
    return context.find_canonical_category(raw_type)
