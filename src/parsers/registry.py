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
from parsers.vendor_config.models import VendorConfig, VendorSection
from parsers.vendor_config.provider import clear_vendor_configs_cache, load_vendor_configs

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


def _vendor_entries(config_provider: ConfigProvider, *, include_disabled: bool) -> list[VendorEntry]:
    """Собрать записи вендоров из конфигов; ``include_disabled`` — брать и отключённых."""
    entries: list[VendorEntry] = []
    for config in load_vendor_configs(config_provider).values():
        if not include_disabled and not config.enabled:
            continue
        entries.extend(
            (BaseParser, _build_parse_config(section, config, config_provider)) for section in config.sections
        )
    return entries


def vendor_entry_for(code: str, config_provider: ConfigProvider) -> VendorEntry:
    """Запись (BaseParser, config) по ИД поставщика (id секции).

    Ищет среди всех загруженных конфигов секцию с указанным ``id``.
    Возвращает первую найденную (включая отключённых).
    """
    for config in load_vendor_configs(config_provider).values():
        for section in config.sections:
            if section.id == code:
                return (BaseParser, _build_parse_config(section, config, config_provider))
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
    return (BaseParser, _build_parse_config(section, config, config_provider))


def clear_registry() -> None:
    """Сбросить кэш конфигов поставщиков (для тестов)."""
    clear_vendor_configs_cache()


def _build_parse_config(
    section: VendorSection, config: VendorConfig, config_provider: ConfigProvider
) -> ParseConfiguration:
    """Построить ParseConfiguration из секции конфига вендора."""
    params = parser_params_from_section(section, config.folder)
    return make_parse_config(params, config_provider=config_provider, vendor_section=section, vendor_config=config)
