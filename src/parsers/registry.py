"""Vendor registry: builds parser entries from ``vendors/*.json`` configs.

Usage::

    from parsers.registry import all_vendors_from_registry, vendor_entry_for

    for parser_cls, parse_config in all_vendors_from_registry():
        ...
"""

from collections.abc import Callable
from typing import Any

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    make_parse_config,
)
from parsers.base_parser.config_driven_parser import (
    parser_params_from_section,
    vendor_markup_policy_from_config,
)
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MarkupPolicy,
    RecommendedOrMapMarkupPolicy,
    make_map_on_opt_markup_policy,
    make_markup_policy,
)
from parsers.vendor_config.models import VendorConfig, VendorSection
from parsers.vendor_config.provider import clear_vendor_configs_cache, load_vendor_configs

# Type aliases (re-exported for convenience)
VendorEntry = tuple[type[BaseParser], ParseConfiguration]


class UnknownVendorError(KeyError):
    """Поставщик с указанным ИД не найден (нет ни одной секции с таким id)."""


def all_vendors_from_registry() -> list[VendorEntry]:
    """Собрать список (BaseParser, config) из конфигов поставщиков (vendors/*.json).

    Каждая секция каждого конфига даёт одну запись.
    Класс парсера — ``BaseParser`` во всех записях; поведение определяется
    стратегиями из конфига, которые хранятся в атрибутах ``ParseConfiguration``.
    """
    entries: list[VendorEntry] = []
    for config in load_vendor_configs().values():
        if not config.enabled:
            continue
        for section in config.sections:
            parse_config = _build_parse_config(section, config.folder)
            # Сохраняем метаданные для config-driven parser
            parse_config._vendor_section = section
            parse_config._vendor_config = config
            entries.append((BaseParser, parse_config))
    return entries


def vendor_entry_for(code: str) -> VendorEntry:
    """Запись (BaseParser, config) по ИД поставщика (id секции).

    Ищет среди всех загруженных конфигов секцию с указанным ``id``.
    Возвращает первую найденную (включая отключённых).
    """
    for config in load_vendor_configs().values():
        for section in config.sections:
            if section.id == code:
                parse_config = _build_parse_config(section, config.folder)
                parse_config._vendor_section = section
                parse_config._vendor_config = config
                return (BaseParser, parse_config)
    raise UnknownVendorError(code)


def vendor_markup_policy_for(
    vendor_cls: type[BaseParser],
    vendor_config: ParseConfiguration,
) -> MarkupPolicy | None:
    """Построить политику наценки по конфигу поставщика.

    В config-driven режиме читает ``pricing`` из секции конфига.
    Для обратной совместимости (легаси-вендоры) читает ``_markup_policy_type``
    атрибут класса вендора.
    """
    section: VendorSection | None = getattr(vendor_config, '_vendor_section', None)
    if isinstance(section, VendorSection):
        return vendor_markup_policy_from_config(section)
    # Fallback для легаси-вендоров: политика из атрибута класса
    policy_type = getattr(vendor_cls, '_markup_policy_type', None)
    if policy_type == 'identity':
        return IdentityMarkupPolicy.create()
    if policy_type == 'map_on_opt':
        return make_map_on_opt_markup_policy(vendor_config)
    if policy_type == 'recommended_or_map':
        return RecommendedOrMapMarkupPolicy.from_config(vendor_config)
    return make_markup_policy(vendor_config)


def make_vendor_entry(
    section: VendorSection,
    config: VendorConfig,
    parse_config: ParseConfiguration | None = None,
) -> VendorEntry:
    """Собрать запись вендора для секции.

    Args:
        section: Секция поставщика.
        config: Конфиг поставщика (folder, behavior).
        parse_config: Готовый ParseConfiguration или None — будет создан.

    Returns:
        (BaseParser, ParseConfiguration) с прикреплёнными метаданными.
    """
    if parse_config is None:
        parse_config = _build_parse_config(section, config.folder)
    parse_config._vendor_section = section
    parse_config._vendor_config = config
    return (BaseParser, parse_config)


# --------------------------------------------------------------------------
# Backward compat: register_vendor — no-op для легаси-вендоров
# (удаляется вместе с src/parsers/vendors/ в этапе 6).
# --------------------------------------------------------------------------

_registry_legacy: dict[str, type] = {}  # noqa: WPS110


def register_vendor(
    code: str,
    *,
    markup_policy: object = None,
) -> Callable[[type[Any]], type[Any]]:
    """No-op decorator для легаси-вендоров (обратная совместимость до сноса)."""

    def wrapper(cls: type[Any]) -> type[Any]:
        cls._markup_policy_type = markup_policy
        _registry_legacy[code] = cls
        return cls

    return wrapper


def clear_registry() -> None:
    """Сбросить кэш конфигов поставщиков и легаси-реестр (для тестов)."""
    clear_vendor_configs_cache()
    _registry_legacy.clear()


def vendor_config_is_enabled(config: ParseConfiguration) -> bool:
    """Поставщик включён (читает ``VendorConfig.enabled``)."""
    vendor_cfg: VendorConfig | None = getattr(config, '_vendor_config', None)
    if isinstance(vendor_cfg, VendorConfig):
        return vendor_cfg.enabled
    return True


def _build_parse_config(section: VendorSection, folder: str) -> ParseConfiguration:
    """Построить ParseConfiguration из секции конфига."""
    params = parser_params_from_section(section, folder)
    return make_parse_config(params)
