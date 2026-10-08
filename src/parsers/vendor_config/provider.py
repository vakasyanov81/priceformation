"""Провайдер конфигов поставщиков: scan parse_config/vendors/*.json с кэшем на папку."""

import re
from functools import lru_cache
from pathlib import Path

from domain.config_context import get_config_provider
from domain.exceptions import ConfigValidationError
from infrastructure.data.file_reader import read_file, read_json_file
from parsers.vendor_config.models import VendorConfig

_VENDORS_FOLDER = 'vendors'
_JSON_SUFFIX = '.json'
_ENABLED_PATTERN = re.compile(r'("enabled"\s*:\s*)([01]|true|false)')


@lru_cache(maxsize=1)
def _load_folder(folder: str) -> dict[str, VendorConfig]:
    """Прочитать все конфиги папки; самой папки нет — пусто (поставщиков пока не настроили)."""
    directory = Path(folder)
    if not directory.is_dir():
        return {}
    configs: dict[str, VendorConfig] = {}
    for path in sorted(directory.glob(f'*{_JSON_SUFFIX}')):
        raw_config = read_json_file(str(path))
        configs[path.stem] = VendorConfig.from_dict(raw_config, path.stem, path.name)
    return configs


def load_vendor_configs() -> dict[str, VendorConfig]:
    """Конфиги всех поставщиков: папка поставщика → конфиг; неизменяемый кэш результата."""
    return _load_folder(get_config_provider().config_file(_VENDORS_FOLDER))


def clear_vendor_configs_cache() -> None:
    """Сбросить кэш конфигов поставщиков (после смены провайдера путей или правки файлов)."""
    _load_folder.cache_clear()


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
