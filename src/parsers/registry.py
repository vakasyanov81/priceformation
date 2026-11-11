"""Vendor registry: builds parser entries from ``vendors/*.json`` configs.

Usage::

    from parsers.registry import all_vendors_from_registry, vendor_entry_for

    for parser_cls, parse_config in all_vendors_from_registry():
        ...
"""

from domain.protocols import ConfigProvider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    make_parse_config,
)
from parsers.base_parser.config_driven_parser import (
    parser_params_from_section,
    vendor_markup_policy_from_config,
)
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.base_parser.routing import VendorRouting
from parsers.vendor_config.group_availability import ensure_groups_available, ensure_section_available
from parsers.vendor_config.group_models import TireAndDiskConfig
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.provider import clear_vendor_configs_cache, load_vendor_configs
from parsers.vendor_config.section_models import VendorSection

# Type aliases (re-exported for convenience)
VendorEntry = tuple[type[BaseParser], ParseConfiguration]


class UnknownVendorError(KeyError):
    """Поставщик с указанным ИД не найден (нет ни одной секции с таким id)."""


def all_vendors_from_registry(config_provider: ConfigProvider) -> list[VendorEntry]:
    """Собрать список (BaseParser, config) только включённых поставщиков (vendors/*.json).

    Каждая секция каждого конфига даёт одну запись.
    Класс парсера — ``BaseParser`` во всех записях; поведение определяется
    стратегиями из конфига, которые хранятся в атрибутах ``ParseConfiguration``.
    """
    return _vendor_entries(config_provider, include_disabled=False)


def all_vendors_including_disabled(config_provider: ConfigProvider) -> list[VendorEntry]:
    """Собрать список (BaseParser, config) всех поставщиков, включая отключённых.

    Отключённые нужны оркестратору: ``BaseParser.parse`` у них вернёт пустой
    список и залогирует предупреждение «поставщик не активен» вместо чтения прайса.
    """
    return _vendor_entries(config_provider, include_disabled=True)


def _supported_sections(config: VendorConfig) -> tuple[VendorSection, ...]:
    """Секции реализованных групп; доступность неподдержанных проверяется отдельно."""
    sections: list[VendorSection] = []
    for group in config.product_groups:
        if isinstance(group, TireAndDiskConfig):
            sections.extend(group.sections)
    return tuple(sections)


def _routing_for(config: VendorConfig) -> VendorRouting | None:
    """Новая схема и явные селекторы используют совместную маршрутизацию поставщика."""
    has_selectors = any(section.row_selector for group in config.product_groups for section in group.sections)
    return VendorRouting(config) if config.configured_groups or has_selectors else None


def _vendor_entries(config_provider: ConfigProvider, *, include_disabled: bool) -> list[VendorEntry]:
    """Собрать записи вендоров из конфигов; ``include_disabled`` — брать и отключённых."""
    entries: list[VendorEntry] = []
    for config in load_vendor_configs(config_provider).values():
        if not include_disabled and not config.enabled:
            continue
        ensure_groups_available(config)
        routing = _routing_for(config)
        entries.extend(
            (BaseParser, _build_parse_config(section, config, config_provider, routing))
            for section in _supported_sections(config)
        )
    return entries


def vendor_entry_for(code: str, config_provider: ConfigProvider) -> VendorEntry:
    """Запись (BaseParser, config) по ИД поставщика (id секции).

    Ищет среди всех загруженных конфигов секцию с указанным ``id``.
    Возвращает первую найденную (включая отключённых).
    """
    for config in load_vendor_configs(config_provider).values():
        ensure_section_available(config, code)
        for section in _supported_sections(config):
            if section.id == code:
                routing = _routing_for(config)
                return (BaseParser, _build_parse_config(section, config, config_provider, routing))
    raise UnknownVendorError(code)


def vendor_markup_policy_for(
    vendor_cls: type[BaseParser],
    vendor_config: ParseConfiguration,
) -> MarkupPolicy | None:
    """Построить политику наценки из конфига секции поставщика.

    Всегда читает ``pricing`` из ``vendor_section`` конфига.
    """
    section = vendor_config.vendor_section
    if section is None:
        return None
    return vendor_markup_policy_from_config(section)


def make_vendor_entry(section: VendorSection, config: VendorConfig, config_provider: ConfigProvider) -> VendorEntry:
    """Собрать запись вендора для секции.

    Args:
        section: Секция поставщика.
        config: Конфиг поставщика (folder, behavior).
        config_provider: Провайдер путей окружения для провайдеров данных (black_list).

    Returns:
        (BaseParser, ParseConfiguration) с прикреплёнными метаданными.
    """
    routing = _routing_for(config)
    return (BaseParser, _build_parse_config(section, config, config_provider, routing))


def clear_registry() -> None:
    """Сбросить кэш конфигов поставщиков (для тестов)."""
    clear_vendor_configs_cache()


def _build_parse_config(
    section: VendorSection,
    config: VendorConfig,
    config_provider: ConfigProvider,
    routing: VendorRouting | None = None,
) -> ParseConfiguration:
    """Построить ParseConfiguration из секции конфига вендора."""
    params = parser_params_from_section(section, config.folder)
    return make_parse_config(
        params, config_provider=config_provider, vendor_section=section, vendor_config=config, routing=routing
    )
