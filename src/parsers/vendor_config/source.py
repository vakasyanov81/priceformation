"""Источник данных поставщика: файлы прайса (по умолчанию) или API из блока «api» конфига."""

from typing import Any

from domain.exceptions import ConfigValidationError
from parsers.data_provider.json_fields import RawConfig, as_config_object, read_object
from parsers.vendor_config.fields import read_text
from parsers.vendor_config.merge import merge_config

SOURCE_FILE = 'xlsx'
SOURCE_API = 'api'
_SOURCE_KEY = 'source'
_API_KEY = 'api'
# Ключи поставщика, которые в режиме API не наследуются: файловые настройки и сам блок `api`.
_VENDOR_ONLY_KEYS = frozenset(('start_row', 'file_templates', 'reader', 'columns', 'sections', _API_KEY))


def select_source(raw: Any, where: str) -> RawConfig:
    """Конфиг для выбранного источника: для «api» блок `api` накладывается на поставщика вместо файлов."""
    payload = as_config_object(raw, where)
    source = read_text(payload, _SOURCE_KEY, where, SOURCE_FILE)
    if source == SOURCE_API:
        return _api_payload(payload, where)
    if source == SOURCE_FILE:
        return _file_payload(payload)
    raise ConfigValidationError(f'{where}: «source» должен быть «xlsx» или «api», получено {source!r}')


def _file_payload(payload: RawConfig) -> RawConfig:
    """Конфиг файлового источника: служебные ключи источника убираются (по умолчанию модель берёт «xlsx»)."""
    file_payload = dict(payload)
    file_payload.pop(_SOURCE_KEY, None)
    file_payload.pop(_API_KEY, None)
    return file_payload


def _api_payload(payload: RawConfig, where: str) -> RawConfig:
    """Конфиг API: настройки поставщика без файловых ключей, поверх — блок `api` (секции, reader, свои слоты)."""
    if _API_KEY not in payload:
        raise ConfigValidationError(f'{where}: при «source»: «api» нужен блок «api»')
    api_block = read_object(payload, _API_KEY, where)
    shared = {key: payload[key] for key in payload if key not in _VENDOR_ONLY_KEYS}
    return merge_config(shared, api_block)
