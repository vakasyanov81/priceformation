"""Проверка внешних ключей до построения реестра и фильтрации активации."""

from collections.abc import Iterator
from dataclasses import dataclass

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.group_models import BatterySection, GroupConfig
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.section_models import VendorSection


@dataclass(frozen=True, slots=True)
class SectionOrigin:
    """Ключ секции и адрес её явного объявления в группе."""

    id: str
    where: str


def validate_group_section_ids(configs: dict[str, VendorConfig]) -> None:
    """Ключ секции уникален среди всех поставщиков и групп."""
    origins: dict[str, SectionOrigin] = {}
    for folder, config in configs.items():
        for origin in _vendor_origins(folder, config):
            _remember_section(origin, origins)


def _remember_section(origin: SectionOrigin, origins: dict[str, SectionOrigin]) -> None:
    """Не разрешать коллизии, включая отключённые группы и поставщиков."""
    previous = origins.get(origin.id)
    if previous is not None:
        raise ConfigValidationError(f'Повторный section.id {origin.id!r}: {previous.where}; {origin.where}')
    origins[origin.id] = origin


def _vendor_origins(folder: str, config: VendorConfig) -> Iterator[SectionOrigin]:
    """Сохранять путь до группы и секции исходного файла."""
    for index, group in enumerate(config.product_groups):
        yield from _group_origins(group, f'{folder}.json → product_groups[{index}].')


def _group_origins(group: GroupConfig, prefix: str) -> Iterator[SectionOrigin]:
    """У каждого ключа сохраняется группа, даже если конфиг отключён."""
    sections: tuple[VendorSection | BatterySection, ...] = group.sections
    for index, section in enumerate(sections):
        yield SectionOrigin(section.id, f'{prefix}sections[{index}].id ({group.id})')
