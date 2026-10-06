"""Примитивы чтения полей конфига поставщика: строки, числа, списки, маппинги.

Расширяет `parsers.data_provider.json_fields` для схемы `parse_config/vendors/*.json`.
"""

from typing import Any

from domain.exceptions import ConfigValidationError
from parsers.data_provider.json_fields import RawConfig


def read_text(payload: RawConfig, key: str, where: str, default: str | None = None) -> str:
    """Прочитать строку; `default=None` — ключ обязателен и не пуст."""
    if key not in payload:
        if default is None:
            raise ConfigValidationError(f'{where}: отсутствует обязательный ключ «{key}»')
        return default
    raw_value: str = payload[key]
    _ensure_text(raw_value, f'{where} → {key}', default is None)
    return raw_value


def _ensure_text(raw_value: Any, where: str, required: bool) -> None:
    """Значение — строка; для обязательного ключа ещё и непустая."""
    if not isinstance(raw_value, str):
        raise ConfigValidationError(f'{where}: ожидается строка, получено {raw_value!r}')
    if required and not raw_value.strip():
        raise ConfigValidationError(f'{where}: ожидается непустая строка, получено {raw_value!r}')


def read_int(payload: RawConfig, key: str, where: str, default: int | None = None) -> int:
    """Прочитать целое; `default=None` — ключ обязателен."""
    if key not in payload:
        if default is None:
            raise ConfigValidationError(f'{where}: отсутствует обязательный ключ «{key}»')
        return default
    return _as_int(payload[key], f'{where} → {key}')


def read_str_list(
    payload: RawConfig,
    key: str,
    where: str,
    default: tuple[str, ...] | None = None,
) -> tuple[str, ...]:
    """Прочитать список строк; `default=None` — ключ обязателен."""
    if key not in payload:
        if default is None:
            raise ConfigValidationError(f'{where}: отсутствует обязательный ключ «{key}»')
        return default
    raw_value = payload[key]
    if not isinstance(raw_value, list):
        raise ConfigValidationError(f'{where} → {key}: ожидается список строк, получено {raw_value!r}')
    for entry in raw_value:
        if not isinstance(entry, str):
            raise ConfigValidationError(f'{where} → {key}: ожидается список строк, получено {raw_value!r}')
    return tuple(raw_value)


def read_int_list(payload: RawConfig, key: str, where: str) -> tuple[int, ...]:
    """Прочитать список целых; ключ отсутствует — пустой кортеж."""
    raw_value = payload.get(key, [])
    if not isinstance(raw_value, list):
        raise ConfigValidationError(f'{where}: «{key}» должно быть списком, получено {raw_value!r}')
    return tuple(_as_int(entry, f'{where} → {key}') for entry in raw_value)


def read_str_map(payload: RawConfig, key: str, where: str) -> dict[str, str]:
    """Прочитать объект строк→строк; ключ отсутствует — пустой объект."""
    raw_value = payload.get(key, {})
    if not isinstance(raw_value, dict):
        raise ConfigValidationError(f'{where}: «{key}» должно быть объектом строк, получено {raw_value!r}')
    for source, target in raw_value.items():
        if not isinstance(source, str) or not isinstance(target, str):
            raise ConfigValidationError(f'{where}: «{key}» должно быть объектом строк, получено {raw_value!r}')
    return raw_value


def _as_int(raw_value: Any, where: str) -> int:
    """Привести значение к целому; bool и дробные без нулевой дробной части — ошибка."""
    if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
        raise ConfigValidationError(f'{where}: ожидается целое, получено {raw_value!r}')
    if not float(raw_value).is_integer():
        raise ConfigValidationError(f'{where}: ожидается целое, получено {raw_value!r}')
    return int(raw_value)
