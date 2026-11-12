"""Модель поставщика с явно объявленными товарными группами."""

from dataclasses import dataclass, replace
from typing import Any

from domain.exceptions import ConfigValidationError
from parsers.data_provider.json_fields import RawConfig, as_config_object
from parsers.vendor_config.common import CommonVendorSettings
from parsers.vendor_config.fields import read_text
from parsers.vendor_config.group_loading import read_group
from parsers.vendor_config.group_models import GroupConfig, TireAndDiskConfig
from parsers.vendor_config.group_schema import read_group_payloads
from parsers.vendor_config.section_models import VendorSection
from parsers.vendor_config.source import SOURCE_FILE

READER_XLS = 'xls'
READER_JSON = 'json'
_READERS = (READER_XLS, READER_JSON)


@dataclass(frozen=True, slots=True)
class VendorConfig:
    """Конфиг поставщика; настройки моделей принадлежат только группам и секциям."""

    folder: str
    code: str
    name: str
    product_groups: tuple[GroupConfig, ...] = ()
    reader: str = READER_XLS
    source: str = SOURCE_FILE
    enabled: bool = True

    @property
    def sections(self) -> tuple[VendorSection, ...]:
        """Шинные секции для существующих каталогов; пусто у поставщика без этой группы."""
        return tuple(
            section
            for group in self.product_groups
            if isinstance(group, TireAndDiskConfig)
            for section in group.sections
        )

    @classmethod
    def from_dict(
        cls, raw: Any, folder: str, where: str, *, common: CommonVendorSettings | None = None
    ) -> VendorConfig:
        """Читать только product_groups; старую схему отклонять с подсказкой переноса."""
        payload = as_config_object(raw, where)
        if 'product_groups' not in payload:
            raise ConfigValidationError(
                f'{where} → product_groups: старый формат больше не поддерживается; '
                'перенесите настройки колонок, стратегий и секций в product_groups '
                'с id tire_and_disk и явными id секций (README.md)'
            )
        return _read_grouped_vendor(payload, folder, where, common or CommonVendorSettings())


def _read_grouped_vendor(payload: RawConfig, folder: str, where: str, common: CommonVendorSettings) -> VendorConfig:
    """Собрать поставщика с независимыми моделями настроек каждой группы."""
    reader = read_text(payload, 'reader', where, READER_XLS)
    if reader not in _READERS:
        raise ConfigValidationError(f'{where} → reader: допустимы xls или json')
    declarations = read_group_payloads(payload, where, common, reads_json=reader == READER_JSON)
    vendor = VendorConfig(
        folder=folder,
        code=read_text(payload, 'code', where),
        name=read_text(payload, 'name', where),
        reader=reader,
        source=read_text(payload, 'source', where, SOURCE_FILE),
    )
    return replace(vendor, product_groups=tuple(read_group(declaration, vendor) for declaration in declarations))
