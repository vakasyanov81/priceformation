"""Провайдер конфигов поставщиков: scan parse_config/vendors/*.json с кэшем на папку.

Файлы с именем на `_` — не поставщики: `_common.json` хранит общие настройки (`common.py`).
"""

import re
from functools import lru_cache
from pathlib import Path

from domain.config_context import get_config_provider
from domain.exceptions import ConfigValidationError
from infrastructure.data.file_reader import read_file, read_json_file
from parsers.vendor_config.common import COMMON_FILE_STEM, CommonVendorSettings
from parsers.vendor_config.merge import merge_config
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.source import select_source

_VENDORS_FOLDER = 'vendors'
_JSON_SUFFIX = '.json'
_SERVICE_PREFIX = '_'
_ENABLED_PATTERN = re.compile(r'("enabled"\s*:\s*)([01]|true|false)')


@lru_cache(maxsize=1)
def _load_common(folder: str) -> CommonVendorSettings:
    """Общие настройки папки; файла нет — пустые (у поставщиков только их собственные настройки)."""
    path = Path(folder) / f'{COMMON_FILE_STEM}{_JSON_SUFFIX}'
    if not path.is_file():
        return CommonVendorSettings()
    return CommonVendorSettings.from_dict(read_json_file(str(path)), path.name)


@lru_cache(maxsize=1)
def _load_folder(folder: str) -> dict[str, VendorConfig]:
    """Прочитать все конфиги папки поверх общих настроек; самой папки нет — пусто (поставщиков не настроили)."""
    directory = Path(folder)
    if not directory.is_dir():
        return {}
    defaults = _load_common(folder).defaults
    configs: dict[str, VendorConfig] = {}
    for path in sorted(directory.glob(f'*{_JSON_SUFFIX}')):
        if path.name.startswith(_SERVICE_PREFIX):
            continue
        raw_config = merge_config(defaults, select_source(read_json_file(str(path)), path.name))
        configs[path.stem] = VendorConfig.from_dict(raw_config, path.stem, path.name)
    return configs


def _vendors_folder() -> str:
    return get_config_provider().config_file(_VENDORS_FOLDER)


def load_vendor_configs() -> dict[str, VendorConfig]:
    """Конфиги всех поставщиков: папка поставщика → конфиг; неизменяемый кэш результата."""
    return _load_folder(_vendors_folder())


def load_common_settings() -> CommonVendorSettings:
    """Общие настройки поставщиков (`vendors/_common.json`)."""
    return _load_common(_vendors_folder())


def clear_vendor_configs_cache() -> None:
    """Сбросить кэш конфигов поставщиков (после смены провайдера путей или правки файлов)."""
    _load_folder.cache_clear()
    _load_common.cache_clear()


def set_vendor_enabled(folder: str, enabled: bool) -> None:
    """Записать флаг enabled в конфиг поставщика, сохранив остальное форматирование файла."""
    path = Path(get_config_provider().config_file(f'{_VENDORS_FOLDER}/{folder}{_JSON_SUFFIX}'))
    replacement = f'\\g<1>{int(enabled)}'
    source = read_file(str(path))
    updated, replaced = _ENABLED_PATTERN.subn(replacement, source, count=1)
    if not replaced:
        raise ConfigValidationError(f'{path.name}: нет поля «enabled» для изменения')
    path.write_text(updated, encoding='utf-8')
    clear_vendor_configs_cache()
