"""Vendor registry: builds parser entries from ``vendors/*.json`` configs.

Usage::

    from parsers.registry import all_vendors_from_registry, vendor_entry_for

    for parser_cls, parse_config in all_vendors_from_registry():
        ...
"""

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


def all_vendors_from_registry() -> list[VendorEntry]:
    """Собрать список (BaseParser, config) только включённых поставщиков (vendors/*.json).

    Каждая секция каждого конфига даёт одну запись.
    Класс парсера — ``BaseParser`` во всех записях; поведение определяется
    стратегиями из конфига, которые хранятся в атрибутах ``ParseConfiguration``.
    """
    return _vendor_entries(include_disabled=False)


def all_vendors_including_disabled() -> list[VendorEntry]:
    """Собрать список (BaseParser, config) всех поставщиков, включая отключённых.

    Отключённые нужны оркестратору: ``BaseParser.parse`` у них вернёт пустой
    список и залогирует предупреждение «поставщик не активен» вместо чтения прайса.
    """
    return _vendor_entries(include_disabled=True)


def _vendor_entries(*, include_disabled: bool) -> list[VendorEntry]:
    """Собрать записи вендоров из конфигов; ``include_disabled`` — брать и отключённых."""
    entries: list[VendorEntry] = []
    for config in load_vendor_configs().values():
        if not include_disabled and not config.enabled:
            continue
        entries.extend((BaseParser, _build_parse_config(section, config)) for section in config.sections)
    return entries


def vendor_entry_for(code: str) -> VendorEntry:
    """Запись (BaseParser, config) по ИД поставщика (id секции).

    Ищет среди всех загруженных конфигов секцию с указанным ``id``.
    Возвращает первую найденную (включая отключённых).
    """
    for config in load_vendor_configs().values():
        for section in config.sections:
            if section.id == code:
                return (BaseParser, _build_parse_config(section, config))
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


def make_vendor_entry(section: VendorSection, config: VendorConfig) -> VendorEntry:
    """Собрать запись вендора для секции.

    Args:
        section: Секция поставщика.
        config: Конфиг поставщика (folder, behavior).

    Returns:
        (BaseParser, ParseConfiguration) с прикреплёнными метаданными.
    """
    return (BaseParser, _build_parse_config(section, config))


def clear_registry() -> None:
    """Сбросить кэш конфигов поставщиков (для тестов)."""
    clear_vendor_configs_cache()


def _build_parse_config(section: VendorSection, config: VendorConfig) -> ParseConfiguration:
    """Построить ParseConfiguration из секции конфига вендора."""
    params = parser_params_from_section(section, config.folder)
    return make_parse_config(params, vendor_section=section, vendor_config=config)
