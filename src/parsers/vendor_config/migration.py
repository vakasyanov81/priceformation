"""Проверяемое преобразование выбранного источника старых настроек без записи файлов."""

from copy import deepcopy

from domain.exceptions import ConfigValidationError
from parsers.data_provider.json_fields import RawConfig, as_config_object, read_object
from parsers.vendor_config.common import CommonVendorSettings
from parsers.vendor_config.group_fields import READING_KEYS, object_list
from parsers.vendor_config.group_schema import LEGACY_KEYS
from parsers.vendor_config.group_validation import MODEL_KEYS
from parsers.vendor_config.models import VendorConfig

_DEFAULTS = 'defaults'


def _settings_for(payload: RawConfig, keys: tuple[str, ...]) -> RawConfig:
    """Выбрать известные настройки без изменения вложенных значений."""
    return {key: payload[key] for key in keys if key in payload}


def migrate_common_config(raw: object, where: str = '_common.json') -> RawConfig:
    """Перенести модельные defaults в tire_and_disk, сохранив очередь эталонов."""
    payload = deepcopy(as_config_object(raw, where))
    CommonVendorSettings.from_dict(payload, where)
    if 'product_groups' in payload:
        return payload
    defaults = read_object(payload, _DEFAULTS, where)
    for key in defaults:
        if key not in (*READING_KEYS, *MODEL_KEYS):
            raise ConfigValidationError(f'{where} → defaults → {key}: настройка не поддерживает перенос')
    payload[_DEFAULTS] = _settings_for(defaults, READING_KEYS)
    payload['product_groups'] = [
        {'id': 'tire_and_disk', _DEFAULTS: _settings_for(defaults, MODEL_KEYS)},
    ]
    CommonVendorSettings.from_dict(payload, where)
    return payload


def migrate_vendor_config(
    raw: object,
    folder: str,
    where: str,
    *,
    common: CommonVendorSettings | None = None,
    section_ids: tuple[str, ...] | None = None,
) -> RawConfig:
    """Преобразовать результат select_source; повторные ID требуют явного решения.

    Полный конфиг с блоком api отклоняется: вызывающий код выбирает и переносит
    каждый источник отдельно. Результат не содержит альтернативного источника;
    его нельзя записывать вместо полного исходного файла с блоком api.
    """
    payload = deepcopy(as_config_object(raw, where))
    if 'api' in payload:
        raise ConfigValidationError(f'{where} → api: перед переносом выберите источник через select_source')
    config = VendorConfig.from_dict(payload, folder, where, common=common)
    if config.configured_groups:
        if section_ids is not None:
            raise ConfigValidationError(f'{where}: section_ids допустимы только для старого формата')
        return payload
    if _DEFAULTS in payload:
        raise ConfigValidationError(f'{where} → defaults: нельзя сочетать новые defaults со старой схемой')
    sections = _migrate_sections(payload, config, where, section_ids)
    group = {key: payload.pop(key) for key in LEGACY_KEYS if key in payload}
    group.update(id='tire_and_disk', sections=sections)
    payload['product_groups'] = [group]
    migrated_common = (
        CommonVendorSettings.from_dict(migrate_common_config({_DEFAULTS: common.defaults}, common.where), common.where)
        if common is not None and not common.group_defaults
        else common
    )
    VendorConfig.from_dict(payload, folder, where, common=migrated_common)
    return payload


def _migrate_sections(
    payload: RawConfig, config: VendorConfig, where: str, section_ids: tuple[str, ...] | None
) -> list[RawConfig]:
    """Сохранить внешние ключи, не генерируя замену для неоднозначных секций."""
    identifiers = section_ids
    if identifiers is None:
        identifiers = tuple(section.id for section in config.sections)
    if len(identifiers) != len(config.sections):
        raise ConfigValidationError(f'{where} → sections: section_ids должен содержать ID каждой секции')
    sections = []
    for index, section in enumerate(object_list(payload.get('sections'), f'{where} → sections')):
        sections.append({**section, 'id': identifiers[index]})
    if len(set(identifiers)) != len(identifiers):
        raise ConfigValidationError(f'{where} → sections: повторные ID; задайте уникальные section_ids явно')
    return sections
