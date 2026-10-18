"""Источник данных поставщика: файлы прайса (по умолчанию) или API из блока «api» конфига."""

from typing import Any

from domain.exceptions import ConfigValidationError
from parsers.data_provider.json_fields import RawConfig, as_config_object, read_object
from parsers.vendor_config.fields import read_text

SOURCE_FILE = 'xlsx'
SOURCE_API = 'api'
_SOURCE_KEY = 'source'
_API_KEY = 'api'
_SHARED_KEYS = ('enabled', 'code', 'name')


def select_source(raw: Any, where: str) -> RawConfig:
    """Конфиг для выбранного источника: для «api» блок `api` заменяет секции и параметры файлов."""
    payload = as_config_object(raw, where)
    source = read_text(payload, _SOURCE_KEY, where, SOURCE_FILE)
    if source == SOURCE_API:
        return _api_payload(payload, where)
    if source == SOURCE_FILE:
        return _file_payload(payload)
    raise ConfigValidationError(f'{where}: «source» должен быть «xlsx» или «api», получено {source!r}')


def _file_payload(payload: RawConfig) -> RawConfig:
    """Конфиг файлового источника: служебные ключи источника убираются."""
    file_payload = dict(payload)
    file_payload.pop(_SOURCE_KEY, None)
    file_payload.pop(_API_KEY, None)
    return file_payload


def _api_payload(payload: RawConfig, where: str) -> RawConfig:
    """Конфиг API: общие поля поставщика и блок `api`, который задаёт секции и reader."""
    if _API_KEY not in payload:
        raise ConfigValidationError(f'{where}: при «source»: «api» нужен блок «api»')
    shared = {key: payload[key] for key in _SHARED_KEYS if key in payload}
    return {**shared, **read_object(payload, _API_KEY, where)}
