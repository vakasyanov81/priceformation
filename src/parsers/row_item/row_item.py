"""
price row item description
"""

import hashlib
import json
from typing import Any, Self
from functools import cache

from parsers.row_item import row_item_formatter as row_format

FIELD_FORMAT = {
    row_format.code: ('code', 'code_man', 'code_art'),
    row_format.money: ("price_opt", "price_recommended", "price_markup"),
    row_format.floated: ("percent_markup",),
    row_format.integer: ("rest_count", "reserve_count", "delivery_period", "slot_count", "group_by_params"),
    row_format.int_or_float: ("ext_diameter", "slot_diameter", "pcd1", "eet", "central_diameter"),
    row_format.boolean: ("double_candidate", "is_double"),
}

DEFAULT_VALUES = {("price_opt", "price_recommended", "price_markup"): 0}


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


class FieldDescriptor:
    """Дескриптор для полей с форматированием"""

    name: str

    def __init__(self, name: str):

        self.formatter = field_format().get(name)
        self.name = name
        default = row_format.text
        self._setter = self.formatter if self.formatter else default

    def __get__(self, instance, owner) -> Self | Any:
        if instance is None:
            return self
        return instance._data.get(self.name) or default_values().get(self.name)

    def __set__(self, instance, value):
        try:
            instance._data[self.name] = self._setter(value)
        except ValueError as err:
            instance._errors[self.name] = {'value': value, 'error': str(err)}


class RowItem:
    """
    price row item description
    """

    # ==== Основные коды и наименования
    code: FieldDescriptor | str = FieldDescriptor('code')
    code_man: FieldDescriptor | str = FieldDescriptor('code_man')
    code_art: FieldDescriptor | str = FieldDescriptor('code_art')
    title: FieldDescriptor | str = FieldDescriptor('title')
    manufacturer: FieldDescriptor | str = FieldDescriptor('manufacturer_name')

    # ==== Цены
    # закупочная цена
    price_opt: FieldDescriptor | float = FieldDescriptor('price_opt')
    # рекомендуемая поставщиком цена
    price_recommended: FieldDescriptor | float = FieldDescriptor('price_recommended')
    # цена с учетом наценки
    price_markup: FieldDescriptor | float = FieldDescriptor('price_markup')
    percent_markup: FieldDescriptor | float = FieldDescriptor('percent_markup')

    # ==== Поставщик и характеристики
    supplier_name: FieldDescriptor | str = FieldDescriptor('supplier_name')
    type_production: FieldDescriptor | str = FieldDescriptor('type_production')
    brand: FieldDescriptor | str = FieldDescriptor('brand')

    # ==== Остатки и сроки
    rest_count: FieldDescriptor | int = FieldDescriptor('rest_count')
    reserve_count: FieldDescriptor | int = FieldDescriptor('reserve_count')
    delivery_period: FieldDescriptor | int = FieldDescriptor('delivery_period')
    condition: FieldDescriptor | str = FieldDescriptor('condition')
    available: FieldDescriptor | int = FieldDescriptor('available')

    # ==== Сезонность и шипы
    season: FieldDescriptor | str = FieldDescriptor('season')
    spike: FieldDescriptor | str = FieldDescriptor('spike')

    # ==== Габариты и параметры шин/дисков
    width: FieldDescriptor | str = FieldDescriptor('width')
    height_percent: FieldDescriptor | str = FieldDescriptor('height_percent')
    mark: FieldDescriptor | str = FieldDescriptor('mark')
    diameter: FieldDescriptor | str = FieldDescriptor('diameter')
    ext_diameter: FieldDescriptor | int | float = FieldDescriptor('ext_diameter')
    # толщина диска
    disk_thickness: FieldDescriptor | str = FieldDescriptor('disk_thickness')
    # кол-во отверстий
    slot_count: FieldDescriptor | int = FieldDescriptor('slot_count')
    slot_diameter: FieldDescriptor | int | float = FieldDescriptor('slot_diameter')
    # американское обозначение принадлежности
    us_aff_designation: FieldDescriptor | str = FieldDescriptor('us_aff_designation')
    # сверловка отверстий в дисках, бывает под один размер бывает универсальный тип под два размера
    pcd1: FieldDescriptor | int | float = FieldDescriptor('pcd1')
    pcd2: FieldDescriptor | int = FieldDescriptor('pcd2')
    eet: FieldDescriptor | int | float = FieldDescriptor('eet')
    central_diameter: FieldDescriptor | int | float = FieldDescriptor('central_diameter')

    # ==== Дополнительные параметры
    color: FieldDescriptor | str = FieldDescriptor('color')
    # основной цвет
    main_color: FieldDescriptor | str = FieldDescriptor('main_color')
    tire_type: FieldDescriptor | str = FieldDescriptor('tire_type')
    # Надпись на боковине
    inscription_on_the_side: FieldDescriptor | int = FieldDescriptor('inscription_on_the_side')
    # Тяжелая шина, можно ехать на спущенной
    run_flat: FieldDescriptor | int = FieldDescriptor('run_flat')
    index_velocity: FieldDescriptor | str = FieldDescriptor('index_velocity')
    index_load: FieldDescriptor | str = FieldDescriptor('index_load')
    model: FieldDescriptor | str = FieldDescriptor('model')
    construction_type: FieldDescriptor | str = FieldDescriptor('construction_type')
    # Ось (ведущая, рулевая...)
    axis: FieldDescriptor | str = FieldDescriptor('axis')
    # слойность
    layering: FieldDescriptor | str = FieldDescriptor('layering')
    # камерность
    intimacy: FieldDescriptor | str = FieldDescriptor('intimacy')
    # наличие и тип камеры
    camera_type: FieldDescriptor | str = FieldDescriptor('camera_type')
    # крепеж
    fastener: FieldDescriptor | int = FieldDescriptor('fastener')
    disk_type: FieldDescriptor | int = FieldDescriptor('disk_type')
    # вид диска - легковой / грузовой
    disk_type_1: FieldDescriptor | int = FieldDescriptor('disk_type_1')
    title_chunks: FieldDescriptor | int = FieldDescriptor('title_chunks')

    # ==== Служебные поля и группировка
    order: FieldDescriptor | int = FieldDescriptor('order')
    # группировка по параметрам, для поиска дублей
    group_by_params: FieldDescriptor | int = FieldDescriptor('group_by_params')
    double_candidate: FieldDescriptor | bool = FieldDescriptor('double_candidate')
    is_double: FieldDescriptor | bool = FieldDescriptor('is_double')

    def __init__(self, item: dict = None):
        """init"""
        item = item or {}
        self._data = {}
        self._errors = {}
        formatters = field_format()

        for key, value in item.items():
            formatter = formatters.get(key)
            try:
                default = row_format.text
                self._data[key] = formatter(value) if formatter else default(value)
            except ValueError as err:
                self._errors[key] = {'value': value, 'error': str(err)}

    @property
    def parse_errors(self) -> dict[str, Any]:
        return self._errors

    @property
    def codes(self) -> list:
        """codes"""
        codes = [self.code, self.code_man, self.code_art]
        return list({code for code in codes if code})

    @property
    def hash_title(self):
        """hash title"""
        if not self.title:
            return None
        return hashlib.md5(self.title.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, dictable_str: str) -> "RowItem":
        """from dict"""
        data = json.loads(dictable_str) if isinstance(dictable_str, str) else dictable_str
        return cls(data)

    def to_dict(self):
        """to dict"""
        return dict(self._data)
