"""
примитивы чтения полей JSON-конфига с проверкой типа
"""

from typing import Any

from domain.exceptions import ConfigValidationError

type RawConfig = dict[str, Any]


def as_config_object(raw: Any, where: str) -> RawConfig:
    """Проверить, что значение — объект."""
    if not isinstance(raw, dict):
        raise ConfigValidationError(f'{where}: ожидается объект, получено {raw!r}')
    return raw


def read_number(raw: RawConfig, key: str, where: str) -> float:
    """Прочитать число с проверкой типа (bool — не число)."""
    raw_value = raw.get(key, 0)
    if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
        raise ConfigValidationError(f'{where}: «{key}» должно быть числом, получено {raw_value!r}')
    return float(raw_value)


def read_flag(raw: RawConfig, key: str, where: str, default: bool = False) -> bool:
    """Прочитать true/false с проверкой типа."""
    raw_value = raw.get(key, default)
    if not isinstance(raw_value, bool):
        raise ConfigValidationError(f'{where}: «{key}» должно быть true/false, получено {raw_value!r}')
    return raw_value


def read_zero_one_flag(raw: RawConfig, key: str, where: str) -> bool:
    """Прочитать флаг, который в JSON записан как 0 или 1."""
    raw_value = raw.get(key)
    if isinstance(raw_value, bool):
        return raw_value
    if not isinstance(raw_value, int) or raw_value not in (0, 1):
        raise ConfigValidationError(f'{where}: «{key}» должен быть 0 или 1, получено {raw_value!r}')
    return bool(raw_value)


def read_object(raw: RawConfig, key: str, where: str) -> RawConfig:
    """Прочитать вложенный объект; ключ отсутствует — пустой объект."""
    section = f'{where} → {key}'
    return as_config_object(raw.get(key, {}), section)


def read_mode(raw: RawConfig, where: str, modes: tuple[str, ...]) -> str:
    """Прочитать режим из `modes`; ключ отсутствует — первый режим."""
    raw_value = raw.get('mode', modes[0])
    if raw_value not in modes:
        allowed = ' или '.join(modes)
        raise ConfigValidationError(f'{where}: «mode» должен быть {allowed}, получено {raw_value!r}')
    return str(raw_value)
