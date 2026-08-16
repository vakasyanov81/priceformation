"""
price row item description
"""

from __future__ import annotations

import hashlib
import json
from functools import cache
from typing import Any, Generic, Self, TypeVar, cast, overload

from parsers.row_item import row_item_formatter as row_format

FIELD_FORMAT = {
    row_format.code: ("code", "code_man", "code_art"),
    row_format.money: ("price_opt", "price_recommended", "price_markup"),
    row_format.floated: ("percent_markup",),
    row_format.integer: ("rest_count", "reserve_count", "delivery_period", "slot_count", "group_by_params"),
    row_format.int_or_float: ("ext_diameter", "pcd1", "eet", "central_diameter"),
    row_format.boolean: ("double_candidate", "is_double"),
}

DEFAULT_VALUES = {("price_opt", "price_recommended", "price_markup"): 0}

_TValue = TypeVar("_TValue")


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


class FieldDescriptor(Generic[_TValue]):
    """Дескриптор для полей с форматированием."""

    name: str

    def __init__(self, name: str) -> None:
        self.formatter = field_format().get(name)
        self.name = name
        default = row_format.text
        self._setter = self.formatter if self.formatter else default

    @overload
    def __get__(self, instance: None, owner: type | None = None) -> Self: ...

    @overload
    def __get__(self, instance: RowItem, owner: type | None = None) -> _TValue: ...

    def __get__(
        self,
        instance: RowItem | None,
        owner: type | None = None,
    ) -> Self | _TValue:
        if instance is None:
            return self
        stored = instance._key_value_store.get(self.name)
        if stored is None:
            stored = default_values().get(self.name)
        return cast(_TValue, stored)

    def __set__(self, instance: RowItem, attr_value: Any) -> None:
        try:
            instance._key_value_store[self.name] = self._setter(attr_value)
        except ValueError as err:
            instance._errors[self.name] = {"value": attr_value, "error": str(err)}


class RowItem:
    """
    price row item description
    """

    # ==== Основные коды и наименования
    code = FieldDescriptor[str]("code")
    code_man = FieldDescriptor[str]("code_man")
    code_art = FieldDescriptor[str]("code_art")
    title = FieldDescriptor[str]("title")
    manufacturer = FieldDescriptor[str]("manufacturer_name")

    # ==== Цены
    # закупочная цена
    price_opt = FieldDescriptor[float]("price_opt")
    # рекомендуемая поставщиком цена
    price_recommended = FieldDescriptor[float]("price_recommended")
    # цена с учетом наценки
    price_markup = FieldDescriptor[float]("price_markup")
    percent_markup = FieldDescriptor[float]("percent_markup")

    # ==== Поставщик и характеристики
    supplier_name = FieldDescriptor[str]("supplier_name")
    type_production = FieldDescriptor[str]("type_production")
    brand = FieldDescriptor[str]("brand")

    # ==== Остатки и сроки
    rest_count = FieldDescriptor[int]("rest_count")
    reserve_count = FieldDescriptor[int]("reserve_count")
    delivery_period = FieldDescriptor[int]("delivery_period")
    condition = FieldDescriptor[str]("condition")
    available = FieldDescriptor[int]("available")

    # ==== Сезонность и шипы
    season = FieldDescriptor[str]("season")
    spike = FieldDescriptor[str]("spike")

    # ==== Габариты и параметры шин/дисков
    width = FieldDescriptor[str]("width")
    height_percent = FieldDescriptor[str]("height_percent")
    mark = FieldDescriptor[str]("mark")
    diameter = FieldDescriptor[str]("diameter")
    ext_diameter = FieldDescriptor[int | float]("ext_diameter")
    # толщина диска
    disk_thickness = FieldDescriptor[str]("disk_thickness")
    # кол-во отверстий
    slot_count = FieldDescriptor[int]("slot_count")
    # американское обозначение принадлежности
    us_aff_designation = FieldDescriptor[str]("us_aff_designation")
    # сверловка отверстий в дисках, бывает под один размер бывает универсальный тип под два размера
    pcd1 = FieldDescriptor[int | float]("pcd1")
    pcd2 = FieldDescriptor[int]("pcd2")
    eet = FieldDescriptor[int | float]("eet")
    central_diameter = FieldDescriptor[int | float]("central_diameter")

    # ==== Дополнительные параметры
    color = FieldDescriptor[str]("color")
    # основной цвет
    main_color = FieldDescriptor[str]("main_color")
    tire_type = FieldDescriptor[str]("tire_type")
    # Надпись на боковине
    inscription_on_the_side = FieldDescriptor[int]("inscription_on_the_side")
    # Тяжелая шина, можно ехать на спущенной
    run_flat = FieldDescriptor[int]("run_flat")
    index_velocity = FieldDescriptor[str]("index_velocity")
    index_load = FieldDescriptor[str]("index_load")
    model = FieldDescriptor[str]("model")
    construction_type = FieldDescriptor[str]("construction_type")
    # Ось (ведущая, рулевая...)
    axis = FieldDescriptor[str]("axis")
    # слойность
    layering = FieldDescriptor[str]("layering")
    # камерность
    intimacy = FieldDescriptor[str]("intimacy")
    # наличие и тип камеры
    camera_type = FieldDescriptor[str]("camera_type")
    # крепеж
    fastener = FieldDescriptor[int]("fastener")
    disk_type = FieldDescriptor[int]("disk_type")
    # вид диска - легковой / грузовой
    disk_type_1 = FieldDescriptor[int]("disk_type_1")
    title_chunks = FieldDescriptor[int]("title_chunks")

    # ==== Служебные поля и группировка
    order = FieldDescriptor[int]("order")
    # группировка по параметрам, для поиска дублей
    group_by_params = FieldDescriptor[int]("group_by_params")
    double_candidate = FieldDescriptor[bool]("double_candidate")
    is_double = FieldDescriptor[bool]("is_double")

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
                self._errors[key] = {"value": attr_value, "error": str(err)}

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
        return hashlib.md5(self.title.encode("utf-8"), usedforsecurity=False).hexdigest()

    @classmethod
    def from_dict(cls, serialized_data: str | dict[str, Any]) -> "RowItem":
        """from dict"""
        parsed_data = json.loads(serialized_data) if isinstance(serialized_data, str) else serialized_data
        return cls(parsed_data)

    def to_dict(self) -> dict[str, Any]:
        """to dict"""
        return dict(self._key_value_store)
