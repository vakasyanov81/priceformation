"""Общие настройки поставщиков: parse_config/vendors/_common.json.

`defaults` — общие настройки чтения; `product_groups` — настройки конкретных моделей.
До миграции поддерживаются старые `defaults` для поставщиков старого формата.
`title_reference_order` — очередь поставщиков-эталонов названия группы дублей (имена файлов без `.json`,
первый — главный эталон).
"""

from dataclasses import dataclass, field
from typing import Any

from domain.product_groups import ProductGroup
from parsers.data_provider.json_fields import RawConfig, as_config_object, read_object
from parsers.vendor_config.fields import read_str_list
from parsers.vendor_config.group_defaults import GroupDefaults, read_group_defaults
from parsers.vendor_config.group_fields import reading_defaults
from parsers.vendor_config.merge import merge_config

COMMON_FILE_STEM = '_common'


@dataclass(frozen=True, slots=True)
class CommonVendorSettings:
    """Общие настройки поставщиков."""

    defaults: RawConfig = field(default_factory=dict)
    title_reference_order: tuple[str, ...] = ()
    group_defaults: tuple[GroupDefaults, ...] = ()
    where: str = '_common.json'

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> CommonVendorSettings:
        """Разобрать `_common.json`."""
        payload = as_config_object(raw, where)
        return cls(
            defaults=(
                reading_defaults(payload, where)
                if 'product_groups' in payload
                else read_object(payload, 'defaults', where)
            ),
            title_reference_order=read_str_list(payload, 'title_reference_order', where, ()),
            group_defaults=read_group_defaults(payload, where),
            where=where,
        )


def legacy_defaults(common: CommonVendorSettings) -> RawConfig:
    """Переходный старый поставщик получает только общие значения шин и дисков."""
    defaults = common.defaults
    for group in common.group_defaults:
        if group.id is ProductGroup.TIRE_AND_DISK:
            defaults = merge_config(defaults, group.defaults)
    return defaults
