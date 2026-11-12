"""Наследование настроек: общий файл → поставщик → секция.

Объекты сливаются по ключам, остальные значения (числа, строки, списки) заменяются целиком.
Карты `columns` и `markup_rules` заменяются целиком: колонки и шкалы разных
уровней не должны смешиваться.
"""

from copy import deepcopy

from parsers.data_provider.json_fields import RawConfig

_REPLACED_KEYS = ('columns', 'markup_rules')


def merge_config(base: RawConfig, override: RawConfig) -> RawConfig:
    """Наложить `override` на `base`; исходные словари не меняются."""
    merged = deepcopy(base)
    for key, overriding in override.items():
        inherited = merged.get(key)
        if isinstance(inherited, dict) and isinstance(overriding, dict) and key not in _REPLACED_KEYS:
            merged[key] = merge_config(inherited, overriding)
        else:
            merged[key] = deepcopy(overriding)
    return merged
