"""Реестр плоских полей строки прайса.

Единственный источник правды сразу для трёх вещей: имя плоского ключа (его
видят шаблоны колонок, jsonl и parse_report), приведение значения к типу поля
и дефолт для незаданного поля. Путь `path` говорит, в каком value object живёт
поле: `tire.width`.

Приведение типов — существующие функции из `row_item_formatter`, новых обёрток
здесь нет.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final

from parsers.row_item import row_item_formatter as row_format

IDENTITY: Final = 'identity'
TIRE: Final = 'tire'
DISK: Final = 'disk'
PRICING: Final = 'pricing'
STOCK: Final = 'stock'
DUPLICATE: Final = 'duplicate'
VENDOR: Final = 'vendor'

_PRICE_DEFAULT: Final = 0


@dataclass(frozen=True, slots=True)
class FieldSpec:
    """Описание одного плоского поля: путь в VO, приведение типа, дефолт."""

    key: str
    path: str
    coercer: Callable[[Any], Any]
    default: Any = None


FIELD_SPECS: Final[tuple[FieldSpec, ...]] = (
    # ==== Производитель, бренд, модель и коды
    FieldSpec('code', f'{IDENTITY}.code', row_format.code),
    FieldSpec('code_man', f'{IDENTITY}.code_man', row_format.code),
    FieldSpec('code_art', f'{IDENTITY}.code_art', row_format.code),
    FieldSpec('title', f'{IDENTITY}.title', row_format.text),
    FieldSpec('manufacturer_name', f'{IDENTITY}.manufacturer', row_format.text),
    FieldSpec('brand', f'{IDENTITY}.brand', row_format.text),
    FieldSpec('model', f'{IDENTITY}.model', row_format.text),
    # ==== Характеристики шин
    FieldSpec('season', f'{TIRE}.season', row_format.text),
    FieldSpec('spike', f'{TIRE}.spike', row_format.text),
    FieldSpec('width', f'{TIRE}.width', row_format.text),
    FieldSpec('height_percent', f'{TIRE}.height_percent', row_format.text),
    FieldSpec('mark', f'{TIRE}.mark', row_format.text),
    FieldSpec('diameter', f'{TIRE}.diameter', row_format.text),
    FieldSpec('ext_diameter', f'{TIRE}.ext_diameter', row_format.int_or_float),
    FieldSpec('us_aff_designation', f'{TIRE}.us_aff_designation', row_format.text),
    FieldSpec('tire_type', f'{TIRE}.tire_type', row_format.text),
    FieldSpec('inscription_on_the_side', f'{TIRE}.inscription_on_the_side', row_format.text),
    FieldSpec('run_flat', f'{TIRE}.run_flat', row_format.text),
    FieldSpec('index_velocity', f'{TIRE}.index_velocity', row_format.text),
    FieldSpec('index_load', f'{TIRE}.index_load', row_format.text),
    FieldSpec('construction_type', f'{TIRE}.construction_type', row_format.text),
    FieldSpec('axis', f'{TIRE}.axis', row_format.text),
    FieldSpec('layering', f'{TIRE}.layering', row_format.text),
    FieldSpec('intimacy', f'{TIRE}.intimacy', row_format.text),
    FieldSpec('camera_type', f'{TIRE}.camera_type', row_format.text),
    # ==== Характеристики дисков
    FieldSpec('disk_thickness', f'{DISK}.disk_thickness', row_format.text),
    FieldSpec('slot_count', f'{DISK}.slot_count', row_format.integer),
    FieldSpec('pcd1', f'{DISK}.pcd1', row_format.int_or_float),
    FieldSpec('pcd2', f'{DISK}.pcd2', row_format.text),
    FieldSpec('eet', f'{DISK}.eet', row_format.int_or_float),
    FieldSpec('central_diameter', f'{DISK}.central_diameter', row_format.int_or_float),
    FieldSpec('fastener', f'{DISK}.fastener', row_format.text),
    FieldSpec('disk_type', f'{DISK}.disk_type', row_format.text),
    FieldSpec('disk_type_1', f'{DISK}.disk_type_1', row_format.text),
    FieldSpec('color', f'{DISK}.color', row_format.text),
    FieldSpec('main_color', f'{DISK}.main_color', row_format.text),
    # ==== Цены и наценки
    FieldSpec('price_opt', f'{PRICING}.price_opt', row_format.money, _PRICE_DEFAULT),
    FieldSpec('price_recommended', f'{PRICING}.price_recommended', row_format.money, _PRICE_DEFAULT),
    FieldSpec('price_markup', f'{PRICING}.price_markup', row_format.money, _PRICE_DEFAULT),
    FieldSpec('percent_markup', f'{PRICING}.percent_markup', row_format.floated),
    # ==== Остатки и сроки
    FieldSpec('rest_count', f'{STOCK}.rest_count', row_format.integer),
    FieldSpec('reserve_count', f'{STOCK}.reserve_count', row_format.integer),
    FieldSpec('delivery_period', f'{STOCK}.delivery_period', row_format.integer),
    FieldSpec('condition', f'{STOCK}.condition', row_format.text),
    FieldSpec('available', f'{STOCK}.available', row_format.text),
    # ==== Служебные поля и группировка
    FieldSpec('order', f'{DUPLICATE}.order', row_format.text),
    FieldSpec('group_by_params', f'{DUPLICATE}.group_by_params', row_format.integer),
    FieldSpec('double_candidate', f'{DUPLICATE}.double_candidate', row_format.boolean),
    FieldSpec('is_double', f'{DUPLICATE}.is_double', row_format.boolean),
    FieldSpec('disputed', f'{DUPLICATE}.disputed', row_format.text),
    # ==== Поставщик и тип товара
    FieldSpec('supplier_name', f'{VENDOR}.supplier_name', row_format.text),
    FieldSpec('type_production', f'{VENDOR}.type_production', row_format.text),
)

FIELD_KEYS: Final[tuple[str, ...]] = tuple(spec.key for spec in FIELD_SPECS)

SPEC_BY_KEY: Final[Mapping[str, FieldSpec]] = MappingProxyType({spec.key: spec for spec in FIELD_SPECS})


def spec_of(key: str) -> FieldSpec | None:
    """Описание плоского поля по его ключу; None — вендорский ключ без описания."""
    return SPEC_BY_KEY.get(key)
