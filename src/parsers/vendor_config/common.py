"""Общие настройки поставщиков: parse_config/vendors/_common.json.

`defaults` — общие настройки чтения; `product_groups` — настройки конкретных моделей.
`title_reference_order` — очередь поставщиков-эталонов названия группы дублей (имена файлов без `.json`,
первый — главный эталон).
"""

from dataclasses import dataclass, field
from typing import Any

from parsers.data_provider.json_fields import RawConfig, as_config_object
from parsers.vendor_config.fields import read_str_list
from parsers.vendor_config.group_defaults import GroupDefaults, read_group_defaults
from parsers.vendor_config.group_fields import reading_defaults

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
            defaults=reading_defaults(payload, where),
            title_reference_order=read_str_list(payload, 'title_reference_order', where, ()),
            group_defaults=read_group_defaults(payload, where),
            where=where,
        )
