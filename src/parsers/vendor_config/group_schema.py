"""Структура нового формата групп до построения моделей настроек."""

from dataclasses import dataclass

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig
from parsers.vendor_config.group_fields import GroupObjects, object_list, read_group_id, reading_defaults
from parsers.vendor_config.merge import merge_config

LEGACY_KEYS = ('columns', 'sections', 'category', 'title', 'pricing', 'behavior', 'start_row', 'file_templates')


@dataclass(frozen=True, slots=True)
class GroupPayload:
    """Объявленная группа и путь её настроек в исходном файле."""

    id: ProductGroup
    settings: RawConfig
    where: str


def read_group_payloads(payload: RawConfig, where: str) -> tuple[GroupPayload, ...]:
    """Проверить объявления и не допустить смешения старой схемы с новой."""
    for key in LEGACY_KEYS:
        if key in payload:
            raise ConfigValidationError(f'{where} → {key}: нельзя сочетать старые настройки с product_groups')
    return _parse_groups(
        object_list(payload.get('product_groups'), f'{where} → product_groups'), reading_defaults(payload, where), where
    )


def _parse_groups(groups: GroupObjects, defaults: RawConfig, where: str) -> tuple[GroupPayload, ...]:
    """Разобрать объявления и затем проверить их уникальность."""
    parsed = tuple(
        _group_payload(group, defaults, f'{where} → product_groups[{index}]') for index, group in enumerate(groups)
    )
    _ensure_unique_groups(parsed)
    return parsed


def _ensure_unique_groups(parsed: tuple[GroupPayload, ...]) -> None:
    """Дубли показывают оба места объявления, не сливая их настройки."""
    origins: dict[ProductGroup, str] = {}
    for declaration in parsed:
        previous = origins.get(declaration.id)
        if previous is not None:
            raise ConfigValidationError(f'{declaration.where}.id: повторная группа; первое объявление {previous}.id')
        origins[declaration.id] = declaration.where


def _group_payload(group: RawConfig, defaults: RawConfig, where: str) -> GroupPayload:
    """Секции обязательны у каждого объявления группы."""
    identifier = read_group_id(group, where)
    object_list(group.get('sections'), f'{where} → sections')
    return GroupPayload(identifier, merge_config(defaults, group), where)
