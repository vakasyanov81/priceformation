"""Реестр плоских полей строки прайса.

Единственный источник правды сразу для трёх вещей: имя плоского ключа (его
видят шаблоны колонок, jsonl и parse_report), приведение значения к типу поля
и дефолт для незаданного поля. Путь `path` говорит, в каком value object живёт
поле: `tire.width`.

Приведение типов — существующие функции из `row_item_formatter`, новых обёрток
здесь нет.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Final

from domain.row_item import row_item_formatter as row_format

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
    """Описание одного плоского поля: где живёт, как приводится, дефолт.

    Группа и имя атрибута хранятся отдельно, а не склеенными в `path`: позиция
    читает и пишет их напрямую, а склеивать строку пришлось бы заново в каждом
    месте.
    """

    key: str
    group: str
    attribute: str
    coercer: Callable[[Any], Any]
    default: Any = None
    _path: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, '_path', f'{self.group}.{self.attribute}')

    @property
    def path(self) -> str:
        """Путь поля в позиции, например `tire.width`: подсказки, тесты, отчёты."""
        return self._path


FIELD_SPECS: Final[tuple[FieldSpec, ...]] = (
    # ==== Производитель, бренд, модель и коды
    FieldSpec('code', IDENTITY, 'code', row_format.code),
    FieldSpec('code_man', IDENTITY, 'code_man', row_format.code),
    FieldSpec('code_art', IDENTITY, 'code_art', row_format.code),
    FieldSpec('title', IDENTITY, 'title', row_format.text),
    FieldSpec('manufacturer_name', IDENTITY, 'manufacturer', row_format.text),
    FieldSpec('brand', IDENTITY, 'brand', row_format.text),
    FieldSpec('model', IDENTITY, 'model', row_format.text),
    # ==== Характеристики шин
    FieldSpec('season', TIRE, 'season', row_format.text),
    FieldSpec('spike', TIRE, 'spike', row_format.text),
    FieldSpec('width', TIRE, 'width', row_format.text),
    FieldSpec('height_percent', TIRE, 'height_percent', row_format.text),
    FieldSpec('mark', TIRE, 'mark', row_format.text),
    FieldSpec('diameter', TIRE, 'diameter', row_format.text),
    FieldSpec('ext_diameter', TIRE, 'ext_diameter', row_format.int_or_float),
    FieldSpec('us_aff_designation', TIRE, 'us_aff_designation', row_format.text),
    FieldSpec('tire_type', TIRE, 'tire_type', row_format.text),
    FieldSpec('inscription_on_the_side', TIRE, 'inscription_on_the_side', row_format.text),
    FieldSpec('run_flat', TIRE, 'run_flat', row_format.text),
    FieldSpec('index_velocity', TIRE, 'index_velocity', row_format.text),
    FieldSpec('index_load', TIRE, 'index_load', row_format.text),
    FieldSpec('construction_type', TIRE, 'construction_type', row_format.text),
    FieldSpec('axis', TIRE, 'axis', row_format.text),
    FieldSpec('layering', TIRE, 'layering', row_format.text),
    FieldSpec('intimacy', TIRE, 'intimacy', row_format.text),
    FieldSpec('camera_type', TIRE, 'camera_type', row_format.text),
    # ==== Характеристики дисков
    FieldSpec('disk_thickness', DISK, 'disk_thickness', row_format.text),
    FieldSpec('slot_count', DISK, 'slot_count', row_format.integer),
    FieldSpec('pcd1', DISK, 'pcd1', row_format.int_or_float),
    FieldSpec('pcd2', DISK, 'pcd2', row_format.text),
    FieldSpec('eet', DISK, 'eet', row_format.int_or_float),
    FieldSpec('central_diameter', DISK, 'central_diameter', row_format.int_or_float),
    FieldSpec('fastener', DISK, 'fastener', row_format.text),
    FieldSpec('disk_type', DISK, 'disk_type', row_format.text),
    FieldSpec('disk_type_1', DISK, 'disk_type_1', row_format.text),
    FieldSpec('color', DISK, 'color', row_format.text),
    FieldSpec('main_color', DISK, 'main_color', row_format.text),
    # ==== Цены и наценки
    FieldSpec('price_opt', PRICING, 'price_opt', row_format.money, _PRICE_DEFAULT),
    FieldSpec('price_recommended', PRICING, 'price_recommended', row_format.money, _PRICE_DEFAULT),
    FieldSpec('price_markup', PRICING, 'price_markup', row_format.money, _PRICE_DEFAULT),
    FieldSpec('percent_markup', PRICING, 'percent_markup', row_format.floated),
    # ==== Остатки и сроки
    FieldSpec('rest_count', STOCK, 'rest_count', row_format.integer),
    FieldSpec('reserve_count', STOCK, 'reserve_count', row_format.integer),
    FieldSpec('delivery_period', STOCK, 'delivery_period', row_format.integer),
    FieldSpec('condition', STOCK, 'condition', row_format.text),
    FieldSpec('available', STOCK, 'available', row_format.text),
    # ==== Служебные поля и группировка
    FieldSpec('order', DUPLICATE, 'order', row_format.text),
    FieldSpec('group_by_params', DUPLICATE, 'group_by_params', row_format.integer),
    FieldSpec('double_candidate', DUPLICATE, 'double_candidate', row_format.boolean),
    FieldSpec('is_double', DUPLICATE, 'is_double', row_format.boolean),
    FieldSpec('disputed', DUPLICATE, 'disputed', row_format.text),
    # ==== Поставщик и тип товара
    FieldSpec('supplier_name', VENDOR, 'supplier_name', row_format.text),
    FieldSpec('type_production', VENDOR, 'type_production', row_format.text),
)

FIELD_KEYS: Final[tuple[str, ...]] = tuple(spec.key for spec in FIELD_SPECS)

SPEC_BY_KEY: Final[Mapping[str, FieldSpec]] = MappingProxyType({spec.key: spec for spec in FIELD_SPECS})


def spec_of(key: str) -> FieldSpec | None:
    """Описание плоского поля по его ключу; None — вендорский ключ без описания."""
    return SPEC_BY_KEY.get(key)
