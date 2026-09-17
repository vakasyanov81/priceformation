"""
price row item description
"""

from __future__ import annotations

import hashlib
import json
from functools import cache
from typing import Any, Self, cast, overload

from parsers.row_item import row_item_formatter as row_format
from parsers.row_item.value_objects import (
    DiskParameters,
    DuplicateInfo,
    Pricing,
    ProductIdentity,
    TireDimensions,
)

PRICE_OPT = 'price_opt'
PRICE_RECOMMENDED = 'price_recommended'
PRICE_MARKUP = 'price_markup'

FIELD_FORMAT = {
    row_format.code: ('code', 'code_man', 'code_art'),
    row_format.money: (PRICE_OPT, PRICE_RECOMMENDED, PRICE_MARKUP),
    row_format.floated: ('percent_markup',),
    row_format.integer: (
        'rest_count',
        'reserve_count',
        'delivery_period',
        'slot_count',
        'group_by_params',
        'order',
    ),
    row_format.int_or_float: (
        'ext_diameter',
        'pcd1',
        'pcd2',
        'eet',
        'central_diameter',
    ),
    row_format.boolean: ('double_candidate', 'is_double'),
}

DEFAULT_VALUES = {(PRICE_OPT, PRICE_RECOMMENDED, PRICE_MARKUP): 0}


def _format_field(attr_value: Any, formatter: Any) -> Any:
    """Применить formatter или text по умолчанию."""
    return formatter(attr_value) if formatter else row_format.text(attr_value)


@cache
def field_format() -> dict[str, Any]:
    fields = {}
    for formatter, list_fields in FIELD_FORMAT.items():
        for field in list_fields:
            fields[field] = formatter
    return fields


@cache
def default_values() -> dict[str, Any]:
    fields = {}
    for list_fields, def_value in DEFAULT_VALUES.items():
        for field in list_fields:
            fields[field] = def_value
    return fields


class FieldDescriptor[TValue]:
    """Дескриптор для полей с форматированием."""

    name: str

    def __init__(self, name: str) -> None:
        self.formatter = field_format().get(name)
        self.name = name
        default = row_format.text
        self._setter = self.formatter if self.formatter else default

    @overload
    def __get__(self, instance: None, _owner: type | None = None) -> Self: ...

    @overload
    def __get__(self, instance: RowItem, _owner: type | None = None) -> TValue: ...

    def __get__(
        self,
        instance: RowItem | None,
        _owner: type | None = None,
    ) -> Self | TValue:
        if instance is None:
            return self
        stored = instance._key_value_store.get(self.name)
        if stored is None:
            stored = default_values().get(self.name)
        return cast(TValue, stored)

    def __set__(self, instance: RowItem, attr_value: Any) -> None:
        try:
            instance._key_value_store[self.name] = self._setter(attr_value)
        except ValueError as err:
            instance._errors[self.name] = {'value': attr_value, 'error': str(err)}


class VOProperty[VOType]:
    """Дескриптор для value-object свойства RowItem."""

    def __init__(self, vo_class: type[VOType]) -> None:
        self.vo_class = vo_class

    @overload
    def __get__(self, instance: None, _owner: type | None = None) -> Self: ...

    @overload
    def __get__(self, instance: RowItem, _owner: type | None = None) -> VOType: ...

    def __get__(
        self,
        instance: RowItem | None,
        _owner: type | None = None,
    ) -> Self | VOType:
        if instance is None:
            return self
        return cast(VOType, self.vo_class.from_flat(instance._key_value_store))  # type: ignore[attr-defined]

    def __set__(self, instance: RowItem, vo: VOType) -> None:
        instance._key_value_store.update(vo.to_flat())  # type: ignore[attr-defined]


class RowItem:
    """
    Строка разобранного прайса.

    Плоские поля доступны напрямую (``row_item.width``, ``row_item.price_opt``).
    Семантические группы — через value-object свойства:

    * ``row_item.tire`` — габариты шины
    * ``row_item.disk`` — параметры диска
    * ``row_item.pricing`` — цены и наценки
    * ``row_item.product_identity`` — производитель/бренд/модель
    * ``row_item.duplicate`` — служебная информация о дублях
    """

    # ==== Основные коды и наименования
    code = FieldDescriptor[str]('code')
    code_man = FieldDescriptor[str]('code_man')
    code_art = FieldDescriptor[str]('code_art')
    title = FieldDescriptor[str]('title')
    manufacturer = FieldDescriptor[str]('manufacturer_name')

    # ==== Цены
    price_opt = FieldDescriptor[float](PRICE_OPT)
    price_recommended = FieldDescriptor[float](PRICE_RECOMMENDED)
    price_markup = FieldDescriptor[float](PRICE_MARKUP)
    percent_markup = FieldDescriptor[float]('percent_markup')

    # ==== Поставщик и характеристики
    supplier_name = FieldDescriptor[str]('supplier_name')
    type_production = FieldDescriptor[str]('type_production')
    brand = FieldDescriptor[str]('brand')

    # ==== Остатки и сроки
    rest_count = FieldDescriptor[int]('rest_count')
    reserve_count = FieldDescriptor[int]('reserve_count')
    delivery_period = FieldDescriptor[int]('delivery_period')
    condition = FieldDescriptor[str]('condition')
    available = FieldDescriptor[int]('available')

    # ==== Сезонность и шипы
    season = FieldDescriptor[str]('season')
    spike = FieldDescriptor[str]('spike')

    # ==== Габариты и параметры шин/дисков
    width = FieldDescriptor[str]('width')
    height_percent = FieldDescriptor[str]('height_percent')
    mark = FieldDescriptor[str]('mark')
    diameter = FieldDescriptor[str]('diameter')
    ext_diameter = FieldDescriptor[int | float]('ext_diameter')
    disk_thickness = FieldDescriptor[str]('disk_thickness')
    slot_count = FieldDescriptor[int]('slot_count')
    us_aff_designation = FieldDescriptor[str]('us_aff_designation')
    pcd1 = FieldDescriptor[int | float]('pcd1')
    pcd2 = FieldDescriptor[int]('pcd2')
    eet = FieldDescriptor[int | float]('eet')
    central_diameter = FieldDescriptor[int | float]('central_diameter')

    # ==== Дополнительные параметры
    color = FieldDescriptor[str]('color')
    main_color = FieldDescriptor[str]('main_color')
    tire_type = FieldDescriptor[str]('tire_type')
    inscription_on_the_side = FieldDescriptor[int]('inscription_on_the_side')
    run_flat = FieldDescriptor[int]('run_flat')
    index_velocity = FieldDescriptor[str]('index_velocity')
    index_load = FieldDescriptor[str]('index_load')
    model = FieldDescriptor[str]('model')
    construction_type = FieldDescriptor[str]('construction_type')
    axis = FieldDescriptor[str]('axis')
    layering = FieldDescriptor[str]('layering')
    intimacy = FieldDescriptor[str]('intimacy')
    camera_type = FieldDescriptor[str]('camera_type')
    fastener = FieldDescriptor[int]('fastener')
    disk_type = FieldDescriptor[int]('disk_type')
    disk_type_1 = FieldDescriptor[int]('disk_type_1')
    title_chunks = FieldDescriptor[int]('title_chunks')

    # ==== Служебные поля и группировка
    order = FieldDescriptor[int]('order')
    group_by_params = FieldDescriptor[int]('group_by_params')
    double_candidate = FieldDescriptor[bool]('double_candidate')
    is_double = FieldDescriptor[bool]('is_double')
    disputed = FieldDescriptor[str]('disputed')

    def __init__(self, raw_row: dict[str, Any] | None = None):
        """init"""
        self._key_value_store: dict[str, Any] = {}
        self._errors: dict[str, Any] = {}
        self._load_raw_row(raw_row or {})

    def _load_raw_row(self, raw_row: dict[str, Any]) -> None:
        """Заполнить store из сырого словаря."""
        formatters = field_format()
        for key, attr_value in raw_row.items():
            try:
                self._key_value_store[key] = _format_field(attr_value, formatters.get(key))
            except ValueError as err:
                self._errors[key] = {'value': attr_value, 'error': str(err)}

    @property
    def parse_errors(self) -> dict[str, Any]:
        return self._errors

    @property
    def codes(self) -> list[str]:
        """codes"""
        codes = [self.code, self.code_man, self.code_art]
        return list({code for code in codes if code})

    @property
    def hash_title(self) -> str | None:
        """hash title"""
        if not self.title:
            return None
        return hashlib.md5(self.title.encode('utf-8'), usedforsecurity=False).hexdigest()

    @classmethod
    def from_dict(cls, serialized_data: str | dict[str, Any]) -> RowItem:
        """from dict"""
        parsed_data = json.loads(serialized_data) if isinstance(serialized_data, str) else serialized_data
        return cls(parsed_data)

    def to_dict(self) -> dict[str, Any]:
        """to dict"""
        return dict(self._key_value_store)

    # ── Value Object accessors ─────────────────────────────────────────

    tire = VOProperty(TireDimensions)
    disk = VOProperty(DiskParameters)
    pricing = VOProperty(Pricing)
    product_identity = VOProperty(ProductIdentity)
    duplicate = VOProperty(DuplicateInfo)
