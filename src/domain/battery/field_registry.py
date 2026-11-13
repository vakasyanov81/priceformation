"""Реестр допустимых входных полей аккумулятора и их преобразований."""

from collections.abc import Callable, Mapping
from decimal import Decimal
from types import MappingProxyType
from typing import Final

from domain.battery import conversions

type BatteryValue = str | int | Decimal | bool | None
type FieldInput = Mapping[str, object]
type Converter[TValue] = Callable[[object], TValue]
type Converters = Mapping[str, Converter[BatteryValue]]

_TEXT_FIELDS = (
    'title',
    'manufacturer_name',
    'model',
    'code',
    'code_art',
    'code_man',
    'current_standard',
    'terminal_type',
    'polarity',
    'size_type',
    'bottom_mount',
    'supplier_name',
    'price_group',
    'certificate_url',
)
_NUMBER_FIELDS = (
    'capacity_ah',
    'starting_current_a',
    'length_mm',
    'width_mm',
    'height_mm',
    'weight',
    'price_opt',
    'price_recommended',
    'price_markup',
)
_FLAG_FIELDS = ('efb', 'agm', 'serviceable')

FIELD_CONVERTERS: Final[Converters] = MappingProxyType(
    {
        **dict.fromkeys(_TEXT_FIELDS, conversions.text),
        **dict.fromkeys(_NUMBER_FIELDS, conversions.number),
        **dict.fromkeys(_FLAG_FIELDS, conversions.flag),
        'rest_count': conversions.stock,
        'warranty_months': conversions.integer,
    }
)
FIELD_KEYS: Final = tuple(FIELD_CONVERTERS)


def validate_fields(fields: FieldInput) -> None:
    """Чужие поля не должны незаметно пропадать при создании аккумулятора."""
    unknown = fields.keys() - FIELD_CONVERTERS.keys()
    if unknown:
        unknown_keys = ', '.join(sorted(unknown))
        raise ValueError(f'Неизвестные поля batteries: {unknown_keys}')


def read_field[TValue](fields: FieldInput, key: str, converter: Converter[TValue]) -> TValue:
    """Дополнить ошибку преобразования именем поля позиции."""
    try:
        return converter(fields.get(key))
    except ValueError as exc:
        raise ValueError(f'{key}: {exc}') from exc
