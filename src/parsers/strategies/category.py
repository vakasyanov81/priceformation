"""
Стратегии слота `category`: назначают `type_production` строки.
"""

from __future__ import annotations

from collections.abc import Mapping

from domain.row_item.row_item import RowItem
from parsers.base_parser.category_finder import canonical_product_type, raw_category_label
from parsers.strategies.protocols import CategoryContext
from parsers.strategies.tire_category import non_tire_product_type
from parsers.vendor_config.slot_configs import CategoryConfig

_CATEGORY_FIELD = 'type_production'
_MANUFACTURER_CHUNK_INDEX = 1
_MANUFACTURER_HEAD_PREFIX = 'автошин'

# Канонизация первого слова строки-заголовка (падеж/число/регистр) к типу товара.
_HEADER_CATEGORIES: Mapping[str, str] = {
    'автошина': 'Автошина',
    'автошины': 'Автошина',
    'автокамера': 'Автокамера',
    'автокамеры': 'Автокамера',
    'диск': 'Диск',
    'диски': 'Диск',
    'ободная': 'Ободная лента',
    'прочие': 'Прочие',
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
    """Категория по значению поля строки через карту (регистр и пробелы нормализуются)."""

    def __init__(self, field_name: str, mapping: Mapping[str, str], default: str) -> None:
        """Запомнить имя поля, карту значений и default."""
        self._field_name = field_name
        self._mapping = mapping
        self._default = default

    @classmethod
    def from_config(cls, config: CategoryConfig) -> FieldMapCategory:
        """Взять поле и карту из конфига."""
        return cls(config.field_name, config.mapping, config.default_value)

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
        """Сопоставить значение поля карте, иначе вернуть default."""
        raw_value = row_item.get_field(self._field_name)
        key = str(raw_value or '').lower().strip()
        return self._mapping.get(key) or self._default


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
        self.current_category: str | None = None

    @classmethod
    def from_config(cls, config: CategoryConfig) -> HeaderRowsCategory:
        """Взять список категорий с нулевым остатком и карту из конфига."""
        return cls(config.zero_rest_categories, config.mapping, config.default_value)

    def resolve(self, row_item: RowItem, context: CategoryContext | None = None) -> str | None:
        """Обновить раздел на строке-заголовке и вернуть тип товара строки."""
        if self._is_header_row(row_item):
            self.current_category = (row_item.identity.title or '').lower().strip()
        if '/' in (self.current_category or ''):
            refined = non_tire_product_type(row_item.identity.title)
            if refined:
                return refined
        return self._first_chunk()

    def is_zero_rest_category(self) -> bool:
        """Относится ли текущий раздел к категориям с обнулённым остатком."""
        lowered = (self.current_category or '').lower()
        return any(name in lowered for name in self._zero_rest_categories)

    def current_manufacturer(self) -> str | None:
        """Производитель из подписи текущего раздела: «автошины triangle» → «triangle»."""
        chunks = (self.current_category or '').split()
        if len(chunks) <= _MANUFACTURER_CHUNK_INDEX or not chunks[0].startswith(_MANUFACTURER_HEAD_PREFIX):
            return None
        return chunks[_MANUFACTURER_CHUNK_INDEX]

    def _first_chunk(self) -> str:
        current = self.current_category or ''
        head = current.split('/')[0]
        chunk = head.split(' ')[0]
        return self._mapping.get(chunk, self._default or chunk)

    def _is_header_row(self, row_item: RowItem) -> bool:
        return bool(row_item.identity.title and not row_item.pricing.price_opt)


def _canonical(raw_type: str | None, context: CategoryContext | None) -> str | None:
    if context is None:
        return canonical_product_type(raw_type)
    return context.find_canonical_category(raw_type)
