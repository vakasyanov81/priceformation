"""Наследование настроек: общий файл → поставщик → секция.

Объекты сливаются по ключам, остальные значения (числа, строки, списки) заменяются целиком.
Исключение — `markup_rules`: карта правил наценки всегда заменяется, иначе правила разных
уровней смешались бы в одну шкалу.
"""

from parsers.data_provider.json_fields import RawConfig

_REPLACED_KEYS = ('markup_rules',)


def merge_config(base: RawConfig, override: RawConfig) -> RawConfig:
    """Наложить `override` на `base`; исходные словари не меняются."""
    merged = dict(base)
    for key, overriding in override.items():
        inherited = merged.get(key)
        if isinstance(inherited, dict) and isinstance(overriding, dict) and key not in _REPLACED_KEYS:
            merged[key] = merge_config(inherited, overriding)
        else:
            merged[key] = overriding
    return merged
