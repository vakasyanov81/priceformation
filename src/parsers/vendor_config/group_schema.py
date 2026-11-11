"""Структура нового формата групп до построения моделей настроек."""

from dataclasses import dataclass

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig
from parsers.vendor_config.common import CommonVendorSettings
from parsers.vendor_config.group_fields import GroupObjects, object_list, read_group_id, reading_defaults
from parsers.vendor_config.group_validation import validate_group_settings
from parsers.vendor_config.merge import merge_config

LEGACY_KEYS = ('columns', 'sections', 'category', 'title', 'pricing', 'behavior', 'start_row', 'file_templates')


@dataclass(frozen=True, slots=True)
class GroupPayload:
    """Объявленная группа и путь её настроек в исходном файле."""

    id: ProductGroup
    settings: RawConfig
    where: str


def read_group_payloads(
    payload: RawConfig, where: str, common: CommonVendorSettings, *, reads_json: bool
) -> tuple[GroupPayload, ...]:
    """Проверить объявления и не допустить смешения старой схемы с новой."""
    for key in LEGACY_KEYS:
        if key in payload:
            raise ConfigValidationError(f'{where} → {key}: нельзя сочетать старые настройки с product_groups')
    groups = object_list(payload.get('product_groups'), f'{where} → product_groups')
    common_defaults = reading_defaults({'defaults': common.defaults}, common.where)
    defaults = reading_defaults(payload, where)
    parsed = _parse_groups(groups, where)
    return tuple(_inherit_group(group, common_defaults, defaults, common, reads_json=reads_json) for group in parsed)


def _parse_groups(groups: GroupObjects, where: str) -> tuple[GroupPayload, ...]:
    """Разобрать объявления и затем проверить их уникальность."""
    parsed = []
    for index, group in enumerate(groups):
        parsed.append(_group_payload(group, where, index))
    _ensure_unique_groups(tuple(parsed))
    return tuple(parsed)


def _ensure_unique_groups(parsed: tuple[GroupPayload, ...]) -> None:
    """Дубли показывают оба места объявления, не сливая их настройки."""
    origins: dict[ProductGroup, str] = {}
    for declaration in parsed:
        previous = origins.get(declaration.id)
        if previous is not None:
            raise ConfigValidationError(f'{declaration.where}.id: повторная группа; первое объявление {previous}.id')
        origins[declaration.id] = declaration.where


def _group_payload(group: RawConfig, where: str, index: int) -> GroupPayload:
    """Секции обязательны у каждого объявления группы."""
    where = f'{where} → product_groups[{index}]'
    identifier = read_group_id(group, where)
    object_list(group.get('sections'), f'{where} → sections')
    return GroupPayload(identifier, group, where)


def _inherit_group(
    group: GroupPayload,
    common_defaults: RawConfig,
    vendor_defaults: RawConfig,
    common: CommonVendorSettings,
    *,
    reads_json: bool,
) -> GroupPayload:
    """Разрешить пять уровней, не создавая групп из общего файла."""
    inherited = common_defaults
    for defaults in common.group_defaults:
        if defaults.id is group.id:
            validate_group_settings(defaults.defaults, f'{defaults.where} → defaults', group.id, reads_json=reads_json)
            inherited = merge_config(inherited, defaults.defaults)
    inherited = merge_config(inherited, vendor_defaults)
    validate_group_settings(group.settings, group.where, group.id, reads_json=reads_json)
    return GroupPayload(group.id, merge_config(inherited, group.settings), group.where)
