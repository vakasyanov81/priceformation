"""Общие настройки поставщиков: parse_config/vendors/_common.json.

`defaults` — настройки в форме конфига поставщика, которые действуют у всех поставщиков: конфиг
поставщика накладывается поверх (объекты сливаются, значения заменяются).
`title_reference_order` — очередь поставщиков-эталонов названия группы дублей (имена файлов без `.json`,
первый — главный эталон).
"""

from dataclasses import dataclass, field
from typing import Any

from parsers.data_provider.json_fields import RawConfig, as_config_object, read_object
from parsers.vendor_config.fields import read_str_list

COMMON_FILE_STEM = '_common'


@dataclass(frozen=True, slots=True)
class CommonVendorSettings:
    """Общие настройки поставщиков."""

    defaults: RawConfig = field(default_factory=dict)
    title_reference_order: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> CommonVendorSettings:
        """Разобрать `_common.json`."""
        payload = as_config_object(raw, where)
        return cls(
            defaults=read_object(payload, 'defaults', where),
            title_reference_order=read_str_list(payload, 'title_reference_order', where, ()),
        )
