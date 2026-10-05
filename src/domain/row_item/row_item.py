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
from dataclasses import dataclass, replace
from typing import Any

from domain.row_item import row_item_formatter as row_format
from domain.row_item.field_registry import FieldSpec, spec_of
from domain.row_item.value_objects import (
    DiskParameters,
    DuplicateInfo,
    Pricing,
    ProductIdentity,
    Stock,
    TireDimensions,
    VendorMeta,
)


class RowField:
    """Плоский ключ поля позиции: с класса — описание (`.name`), с позиции — ничего.

    Имена полей читают шаблоны колонок (`RowItem.price_markup.name`), маппинги
    колонок вендоров и jsonl_codes, поэтому доступ с класса остаётся всегда.

    С самой позиции поле не читается и не пишется: значение лежит в value
    objects (`row.pricing.price_markup`), а запись идёт через `set_field`,
    которая приводит тип, помнит порядок ключей и пишет ошибки разбора. Ключ
    вместо значения молча вернул бы неверные данные, поэтому дескриптор на
    позиции бросает AttributeError с подсказкой.
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

    @property
    def _hint(self) -> str:
        spec = self._spec
        return f'Плоский доступ поля снят: читать {spec.path}, писать row.set_field({spec.key!r}, ...).'

    def __get__(self, instance: RowItem | None, _owner: type | None = None) -> RowField:
        if instance is not None:
            raise AttributeError(self._hint)
        return self

    def __set__(self, instance: RowItem, attr_value: Any) -> None:
        raise AttributeError(self._hint)


@dataclass(eq=False, init=False)
class RowItem:
    """Позиция прайса: value objects, вендорские колонки и ошибки разбора."""

    identity: ProductIdentity
    tire: TireDimensions
    disk: DiskParameters
    pricing: Pricing
    stock: Stock
    duplicate: DuplicateInfo
    vendor: VendorMeta
    extra: dict[str, Any]
    _errors: dict[str, Any]
    _set_keys: dict[str, None]

    # ==== Плоские ключи полей: их читают шаблоны, маппинги колонок и jsonl
    # (RowItem.price_markup.name). Значения лежат в value objects выше.
    code = RowField('code')
    code_man = RowField('code_man')
    code_art = RowField('code_art')
    title = RowField('title')
    manufacturer = RowField('manufacturer_name')
    brand = RowField('brand')
    model = RowField('model')

    price_opt = RowField('price_opt')
    price_recommended = RowField('price_recommended')
    price_markup = RowField('price_markup')
    percent_markup = RowField('percent_markup')

    supplier_name = RowField('supplier_name')
    type_production = RowField('type_production')

    rest_count = RowField('rest_count')
    reserve_count = RowField('reserve_count')
    delivery_period = RowField('delivery_period')
    condition = RowField('condition')
    available = RowField('available')

    season = RowField('season')
    spike = RowField('spike')

    width = RowField('width')
    height_percent = RowField('height_percent')
    mark = RowField('mark')
    diameter = RowField('diameter')
    ext_diameter = RowField('ext_diameter')
    disk_thickness = RowField('disk_thickness')
    slot_count = RowField('slot_count')
    us_aff_designation = RowField('us_aff_designation')
    pcd1 = RowField('pcd1')
    pcd2 = RowField('pcd2')
    eet = RowField('eet')
    central_diameter = RowField('central_diameter')

    color = RowField('color')
    main_color = RowField('main_color')
    tire_type = RowField('tire_type')
    inscription_on_the_side = RowField('inscription_on_the_side')
    run_flat = RowField('run_flat')
    index_velocity = RowField('index_velocity')
    index_load = RowField('index_load')
    construction_type = RowField('construction_type')
    axis = RowField('axis')
    layering = RowField('layering')
    intimacy = RowField('intimacy')
    camera_type = RowField('camera_type')
    fastener = RowField('fastener')
    disk_type = RowField('disk_type')
    disk_type_1 = RowField('disk_type_1')

    order = RowField('order')
    group_by_params = RowField('group_by_params')
    double_candidate = RowField('double_candidate')
    is_double = RowField('is_double')
    disputed = RowField('disputed')

    def __init__(self, raw_row: dict[str, Any] | None = None):
        """init"""
        self.identity = ProductIdentity()
        self.tire = TireDimensions()
        self.disk = DiskParameters()
        self.pricing = Pricing()
        self.stock = Stock()
        self.duplicate = DuplicateInfo()
        self.vendor = VendorMeta()
        self.extra = {}
        self._errors = {}
        self._set_keys = {}
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
        return getattr(getattr(self, spec.group), spec.attribute)

    def _write_spec(self, spec: FieldSpec, attr_value: Any) -> None:
        """Положить приведённое значение в value object, описанное в реестре."""
        current = getattr(self, spec.group)
        setattr(self, spec.group, replace(current, **{spec.attribute: attr_value}))

    @property
    def parse_errors(self) -> dict[str, Any]:
        """Поля, которые не удалось привести к своему типу."""
        return dict(self._errors)

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

    def to_dict(self) -> dict[str, Any]:
        """to dict"""
        row: dict[str, Any] = {}
        for key in self._set_keys:
            row[key] = self.get_field(key)
        return row
