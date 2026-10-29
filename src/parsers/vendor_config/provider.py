"""Провайдер конфигов поставщиков: scan parse_config/vendors/*.json с кэшем на папку.

Файлы с именем на `_` — не поставщики: `_common.json` хранит общие настройки (`common.py`).
Статус активации (`enabled`) живёт отдельно, в `parse_config/vendor_activation.json` (`activation.py`).
"""

from functools import lru_cache
from pathlib import Path

from domain.exceptions import ConfigValidationError
from domain.protocols import ConfigProvider
from infrastructure.data.file_reader import read_json_file
from parsers.data_provider.json_fields import RawConfig
from parsers.vendor_config.activation import apply_activation, load_activation
from parsers.vendor_config.common import COMMON_FILE_STEM, CommonVendorSettings
from parsers.vendor_config.merge import merge_config
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.source import select_source

_VENDORS_FOLDER = 'vendors'
_JSON_SUFFIX = '.json'
_SERVICE_PREFIX = '_'
_ENABLED_KEY = 'enabled'


@lru_cache(maxsize=1)
def _load_common(folder: str) -> CommonVendorSettings:
    """Общие настройки папки; файла нет — пустые (у поставщиков только их собственные настройки)."""
    path = Path(folder) / f'{COMMON_FILE_STEM}{_JSON_SUFFIX}'
    if not path.is_file():
        return CommonVendorSettings()
    return CommonVendorSettings.from_dict(read_json_file(str(path)), path.name)


def _read_vendor(path: Path, defaults: RawConfig) -> VendorConfig:
    """Конфиг одного поставщика поверх общих настроек; `enabled` в нём запрещён — статус в vendor_activation.json."""
    raw_config = merge_config(defaults, select_source(read_json_file(str(path)), path.name))
    if _ENABLED_KEY in raw_config:
        raise ConfigValidationError(f'{path.name}: «enabled» перенесён в vendor_activation.json, уберите поле')
    return VendorConfig.from_dict(raw_config, path.stem, path.name)


@lru_cache(maxsize=1)
def _load_folder(folder: str) -> dict[str, VendorConfig]:
    """Прочитать все конфиги папки поверх общих настроек; самой папки нет — пусто (поставщиков не настроили)."""
    directory = Path(folder)
    if not directory.is_dir():
        return {}
    defaults = _load_common(folder).defaults
    return {
        path.stem: _read_vendor(path, defaults)
        for path in sorted(directory.glob(f'*{_JSON_SUFFIX}'))
        if not path.name.startswith(_SERVICE_PREFIX)
    }


def _vendors_folder(config_provider: ConfigProvider) -> str:
    return config_provider.config_file(_VENDORS_FOLDER)


def load_vendor_configs(config_provider: ConfigProvider) -> dict[str, VendorConfig]:
    """Конфиги всех поставщиков со статусом активации: папка поставщика → конфиг."""
    return apply_activation(_load_folder(_vendors_folder(config_provider)), load_activation(config_provider))


def load_common_settings(config_provider: ConfigProvider) -> CommonVendorSettings:
    """Общие настройки поставщиков (`vendors/_common.json`)."""
    return _load_common(_vendors_folder(config_provider))


def clear_vendor_configs_cache() -> None:
    """Сбросить кэш конфигов поставщиков (после смены провайдера путей или правки файлов)."""
    _load_folder.cache_clear()
    _load_common.cache_clear()
