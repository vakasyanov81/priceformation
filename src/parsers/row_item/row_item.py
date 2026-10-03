"""Позиция прайса: value objects поверх плоского словаря сериализации.

Плоский словарь — контракт сериализации: его видят шаблоны колонок, jsonl и
JSON-отчёт, поэтому `to_dict()` отдаёт ровно те же ключи и в том же порядке,
что и раньше. Хранит же позиция семантические группы (`identity`, `tire`,
`disk`, `pricing`, `stock`, `duplicate`, `vendor`), а порядок ключей помнит
`_set_keys`.

`_errors` живёт снаружи value objects: он накапливается при разборе строки и
не является частью данных позиции. Ключи, которым нет описания в реестре,
вендорские — они лежат в `extra` и доезжают до `to_dict()` как есть.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import MISSING, dataclass, field, fields, replace
from typing import Any, Self, cast, overload

from parsers.row_item import row_item_formatter as row_format
from parsers.row_item.field_registry import FieldSpec, spec_of
from parsers.row_item.value_objects import (
    DiskParameters,
    DuplicateInfo,
    Pricing,
    ProductIdentity,
    Stock,
    TireDimensions,
    VendorMeta,
)


class RowField[TValue]:
    """Поле позиции: на классе — описание (`.name`), на позиции — значение.

    Имена полей читают шаблоны колонок (`RowItem.price_markup.name`) и
    jsonl_codes, поэтому доступ с класса остаётся всегда. Плоский доступ с
    позиции — совместимость, её снимают переносом вызовов на `row.<vo>.<field>`.
    """

    __slots__ = ('_spec',)

    def __init__(self, key: str) -> None:
        spec = spec_of(key)
        if spec is None:
            raise KeyError(key)
        self._spec = spec

    @property
    def name(self) -> str:
        """Плоский ключ поля: так его видят шаблоны и jsonl."""
        return self._spec.key

    @overload
    def __get__(self, instance: None, _owner: type | None = None) -> Self: ...

    @overload
    def __get__(self, instance: RowItem, _owner: type | None = None) -> TValue: ...

    def __get__(self, instance: RowItem | None, _owner: type | None = None) -> Self | TValue:
        if instance is None:
            return self
        return cast(TValue, instance.get_field(self._spec.key))

    def __set__(self, instance: RowItem, attr_value: Any) -> None:
        instance.set_field(self._spec.key, attr_value)


@dataclass(eq=False, init=False)
class RowItem:
    """Позиция прайса: value objects, вендорские колонки и ошибки разбора."""

    identity: ProductIdentity = field(default_factory=ProductIdentity)
    tire: TireDimensions = field(default_factory=TireDimensions)
    disk: DiskParameters = field(default_factory=DiskParameters)
    pricing: Pricing = field(default_factory=Pricing)
    stock: Stock = field(default_factory=Stock)
    duplicate: DuplicateInfo = field(default_factory=DuplicateInfo)
    vendor: VendorMeta = field(default_factory=VendorMeta)
    extra: dict[str, Any] = field(default_factory=dict)
    _errors: dict[str, Any] = field(default_factory=dict, repr=False)
    _set_keys: dict[str, None] = field(default_factory=dict, repr=False)

    # ==== Совместимый плоский доступ: RowItem.price_markup.name для шаблонов
    # и row_item.price_markup для существующих вызовов. Переносится на VO.
    code = RowField[str]('code')
    code_man = RowField[str]('code_man')
    code_art = RowField[str]('code_art')
    title = RowField[str]('title')
    manufacturer = RowField[str]('manufacturer_name')
    brand = RowField[str]('brand')
    model = RowField[str]('model')

    price_opt = RowField[float]('price_opt')
    price_recommended = RowField[float]('price_recommended')
    price_markup = RowField[float]('price_markup')
    percent_markup = RowField[float]('percent_markup')

    supplier_name = RowField[str]('supplier_name')
    type_production = RowField[str]('type_production')

    rest_count = RowField[int]('rest_count')
    reserve_count = RowField[int]('reserve_count')
    delivery_period = RowField[int]('delivery_period')
    condition = RowField[str]('condition')
    available = RowField[int]('available')

    season = RowField[str]('season')
    spike = RowField[str]('spike')

    width = RowField[str]('width')
    height_percent = RowField[str]('height_percent')
    mark = RowField[str]('mark')
    diameter = RowField[str]('diameter')
    ext_diameter = RowField[int | float]('ext_diameter')
    disk_thickness = RowField[str]('disk_thickness')
    slot_count = RowField[int]('slot_count')
    us_aff_designation = RowField[str]('us_aff_designation')
    pcd1 = RowField[int | float]('pcd1')
    pcd2 = RowField[int]('pcd2')
    eet = RowField[int | float]('eet')
    central_diameter = RowField[int | float]('central_diameter')

    color = RowField[str]('color')
    main_color = RowField[str]('main_color')
    tire_type = RowField[str]('tire_type')
    inscription_on_the_side = RowField[int]('inscription_on_the_side')
    run_flat = RowField[int]('run_flat')
    index_velocity = RowField[str]('index_velocity')
    index_load = RowField[str]('index_load')
    construction_type = RowField[str]('construction_type')
    axis = RowField[str]('axis')
    layering = RowField[str]('layering')
    intimacy = RowField[str]('intimacy')
    camera_type = RowField[str]('camera_type')
    fastener = RowField[int]('fastener')
    disk_type = RowField[int]('disk_type')
    disk_type_1 = RowField[int]('disk_type_1')

    order = RowField[int]('order')
    group_by_params = RowField[int]('group_by_params')
    double_candidate = RowField[bool]('double_candidate')
    is_double = RowField[bool]('is_double')
    disputed = RowField[str]('disputed')

    def __init__(self, raw_row: dict[str, Any] | None = None):
        """init"""
        for entry in fields(self):
            factory = entry.default_factory
            setattr(self, entry.name, entry.default if factory is MISSING else factory())
        self._load_raw_row(raw_row or {})

    def _load_raw_row(self, raw_row: dict[str, Any]) -> None:
        """Заполнить позицию из сырого словаря."""
        for key, attr_value in raw_row.items():
            self.set_field(key, attr_value)

    def set_field(self, key: str, attr_value: Any) -> None:
        """Записать значение по плоскому ключу: привести тип и запомнить ключ."""
        spec = spec_of(key)
        try:
            coerced = spec.coercer(attr_value) if spec else row_format.text(attr_value)
        except ValueError as err:
            self._errors[key] = {'value': attr_value, 'error': str(err)}
            return

        self._set_keys[key] = None
        if spec is None:
            self.extra[key] = coerced
            return
        self._write_spec(spec, coerced)

    def get_field(self, key: str) -> Any:
        """Значение по плоскому ключу; у незаданного поля — дефолт реестра."""
        spec = spec_of(key)
        if spec is None:
            return self.extra.get(key)
        group, _, attribute = spec.path.partition('.')
        return getattr(getattr(self, group), attribute)

    def _write_spec(self, spec: FieldSpec, attr_value: Any) -> None:
        """Положить приведённое значение в value object по пути из реестра."""
        group, _, attribute = spec.path.partition('.')
        current = getattr(self, group)
        setattr(self, group, replace(current, **{attribute: attr_value}))

    @property
    def parse_errors(self) -> dict[str, Any]:
        """Поля, которые не удалось привести к своему типу."""
        return self._errors

    @property
    def codes(self) -> list[str]:
        """codes"""
        codes = [self.identity.code, self.identity.code_man, self.identity.code_art]
        return list({code for code in codes if code})

    @property
    def hash_title(self) -> str | None:
        """hash title"""
        if not self.identity.title:
            return None
        title = self.identity.title
        return hashlib.md5(title.encode('utf-8'), usedforsecurity=False).hexdigest()

    @classmethod
    def from_dict(cls, serialized_data: str | dict[str, Any]) -> RowItem:
        """from dict"""
        parsed_data = json.loads(serialized_data) if isinstance(serialized_data, str) else serialized_data
        return cls(parsed_data)

    def to_dict(self) -> dict[str, Any]:
        """to dict"""
        row: dict[str, Any] = {}
        for key in self._set_keys:
            row[key] = self.get_field(key)
        return row
