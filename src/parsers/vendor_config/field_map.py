"""Чтение карт «ключ конфига → поля позиции»: подстрока/категория → значения полей."""

from typing import Any

from domain.exceptions import ConfigValidationError
from domain.row_item.field_registry import spec_of
from parsers.data_provider.json_fields import RawConfig, as_config_object

type FieldMap = dict[str, dict[str, str]]


def read_field_map(payload: RawConfig, key: str, where: str) -> FieldMap:
    """Разобрать карту `key`: подстрока/категория → известные поля позиции со значениями."""
    section = f'{where} → {key}'
    raw_map = _raw_map(payload, key, section)
    return {name: _read_fields(name, raw_fields, section) for name, raw_fields in raw_map.items()}


def _raw_map(payload: RawConfig, key: str, section: str) -> dict[str, Any]:
    """Объект карты из конфига; иначе ошибка с путём."""
    raw_map = payload.get(key, {})
    if not isinstance(raw_map, dict):
        raise ConfigValidationError(f'{section}: ожидается объект, получено {raw_map!r}')
    return raw_map


def _read_fields(name: Any, raw_fields: Any, section: str) -> dict[str, str]:
    """Поля одного ключа карты; ключ — непустая строка."""
    _ensure_name(name, section)
    entry_section = f'{section} → {name}'
    return _read_entry_fields(as_config_object(raw_fields, entry_section), entry_section)


def _ensure_name(name: Any, section: str) -> None:
    """Ключ карты — непустая строка (сравнение без учёта регистра)."""
    if not isinstance(name, str) or not name.strip():
        raise ConfigValidationError(f'{section}: ключ — непустая строка, получено {name!r}')


def _read_entry_fields(fields: RawConfig, section: str) -> dict[str, str]:
    """Поля записи: известные в реестре RowItem ключи со строковыми значениями."""
    parsed: dict[str, str] = {}
    for key, field_value in fields.items():
        if spec_of(key) is None:
            raise ConfigValidationError(
                f'{section}: неизвестное поле «{key}»; ожидается ключ из реестра полей RowItem',
            )
        if not isinstance(field_value, str):
            raise ConfigValidationError(f'{section} → {key}: ожидается строка, получено {field_value!r}')
        parsed[key] = field_value
    return parsed
