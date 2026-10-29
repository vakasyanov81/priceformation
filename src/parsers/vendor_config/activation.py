"""Статус активации поставщиков: `parse_config/vendor_activation.json` (в .gitignore).

Ключ — имя папки поставщика, значение — 0 или 1. Записи нет — поставщик включён.
"""

import json
from dataclasses import replace
from pathlib import Path

from domain.protocols import ConfigProvider
from infrastructure.data.file_reader import read_json_file
from parsers.data_provider.json_fields import as_config_object, read_zero_one_flag
from parsers.vendor_config.models import VendorConfig

_ACTIVATION_FILE = 'vendor_activation.json'


def activation_file(config_provider: ConfigProvider) -> str:
    """Путь к файлу статусов активации в parse_config."""
    return config_provider.config_file(_ACTIVATION_FILE)


def load_activation(config_provider: ConfigProvider) -> dict[str, bool]:
    """Статусы из файла по имени папки; файла нет — пусто."""
    path = Path(activation_file(config_provider))
    if not path.is_file():
        return {}
    raw = as_config_object(read_json_file(str(path)), path.name)
    return {folder: read_zero_one_flag(raw, folder, path.name) for folder in raw}


def apply_activation(
    configs: dict[str, VendorConfig],
    statuses: dict[str, bool],
) -> dict[str, VendorConfig]:
    """Проставить поставщикам статус активации; без записи статус — включён."""
    activated: dict[str, VendorConfig] = {}
    for folder, config in configs.items():
        enabled = statuses.get(folder, True)
        activated[folder] = replace(config, enabled=enabled)
    return activated


def set_vendor_enabled(folder: str, enabled: bool, config_provider: ConfigProvider) -> None:
    """Записать статус активации поставщика в `vendor_activation.json`, остальные статусы сохранить."""
    path = Path(activation_file(config_provider))
    statuses = {**load_activation(config_provider), folder: enabled}
    ordered = dict(sorted(statuses.items()))
    text = json.dumps(ordered, ensure_ascii=False, indent=2)
    path.write_text(f'{text}\n', encoding='utf-8')
