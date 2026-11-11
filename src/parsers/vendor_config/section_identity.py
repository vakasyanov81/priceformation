"""Проверка внешних ключей до построения реестра и фильтрации активации."""

from collections.abc import Iterator
from dataclasses import dataclass

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.group_models import BatterySection, GroupConfig
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.section_models import VendorSection


@dataclass(frozen=True, slots=True)
class SectionOrigin:
    """Ключ и адрес секции; старые неявные ключи сохраняются до миграции."""

    id: str
    where: str
    grouped: bool


def validate_group_section_ids(configs: dict[str, VendorConfig]) -> None:
    """Новая секция не может повторять ключ ни новой, ни старой секции."""
    origins: dict[str, SectionOrigin] = {}
    for folder, config in configs.items():
        for origin in _vendor_origins(folder, config):
            _remember_section(origin, origins)


def _remember_section(origin: SectionOrigin, origins: dict[str, SectionOrigin]) -> None:
    """Не разрешать коллизии новых ключей; старые конфиги пока совместимы."""
    previous = origins.get(origin.id)
    if previous is not None and (origin.grouped or previous.grouped):
        raise ConfigValidationError(f'Повторный section.id {origin.id!r}: {previous.where}; {origin.where}')
    origins[origin.id] = origin


def _vendor_origins(folder: str, config: VendorConfig) -> Iterator[SectionOrigin]:
    """Пути сохраняют исходное расположение секций каждого формата."""
    for index, group in enumerate(config.product_groups):
        prefix = f'product_groups[{index}].' if config.configured_groups else ''
        yield from _group_origins(group, f'{folder}.json → {prefix}', bool(config.configured_groups))


def _group_origins(group: GroupConfig, prefix: str, grouped: bool) -> Iterator[SectionOrigin]:
    """У каждого ключа сохраняется группа, даже если конфиг отключён."""
    sections: tuple[VendorSection | BatterySection, ...] = group.sections
    for index, section in enumerate(sections):
        yield SectionOrigin(section.id, f'{prefix}sections[{index}].id ({group.id})', grouped)
