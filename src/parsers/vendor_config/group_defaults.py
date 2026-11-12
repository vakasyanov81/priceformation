"""Общие настройки конкретных групп не объявляют секции поставщика."""

from dataclasses import dataclass

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig, read_object
from parsers.vendor_config.group_fields import READING_KEYS, object_list, read_group_id
from parsers.vendor_config.group_validation import MODEL_KEYS, validate_group_settings


@dataclass(frozen=True, slots=True)
class GroupDefaults:
    """Исходные значения и их адрес для диагностики до слияния."""

    id: ProductGroup
    defaults: RawConfig
    where: str


def read_group_defaults(payload: RawConfig, where: str) -> tuple[GroupDefaults, ...]:
    """Прочитать необязательный список уникальных групп общего файла."""
    raw_groups = payload.get('product_groups', [])
    if isinstance(raw_groups, list) and not raw_groups:
        return ()
    groups = object_list(raw_groups, f'{where} → product_groups')
    parsed = []
    for index, group in enumerate(groups):
        parsed.append(_read_defaults(group, where, index))
    _ensure_unique(tuple(parsed))
    return tuple(parsed)


def _ensure_unique(groups: tuple[GroupDefaults, ...]) -> None:
    """Показать обе исходные записи при повторении группы."""
    origins: dict[ProductGroup, str] = {}
    for group in groups:
        previous = origins.get(group.id)
        if previous is not None:
            raise ConfigValidationError(f'{group.where}.id: повторная группа; первое объявление {previous}.id')
        origins[group.id] = group.where


def _read_defaults(group: RawConfig, where: str, index: int) -> GroupDefaults:
    """Проверить оболочку группы и её собственную область настроек."""
    where = f'{where} → product_groups[{index}]'
    identifier = read_group_id(group, where)
    _check_keys(group, ('id', 'defaults'), where)
    defaults_where = f'{where} → defaults'
    defaults = read_object(group, 'defaults', where)
    _check_keys(defaults, (*READING_KEYS, *MODEL_KEYS), defaults_where)
    validate_group_settings(defaults, defaults_where, identifier, reads_json=True)
    return GroupDefaults(identifier, defaults, where)


def _check_keys(payload: RawConfig, allowed: tuple[str, ...], where: str) -> None:
    """Структура и маршруты не являются наследуемыми настройками."""
    for key in payload:
        if key not in allowed:
            raise ConfigValidationError(f'{where} → {key}: недопустимая настройка общих значений группы')
