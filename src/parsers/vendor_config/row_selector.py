"""Явный селектор исходных строк секции поставщика."""

from dataclasses import dataclass
from typing import Any

from domain.exceptions import ConfigValidationError
from parsers.data_provider.json_fields import RawConfig, as_config_object
from parsers.vendor_config.fields import read_str_list, read_text


@dataclass(frozen=True, slots=True)
class RowSelector:
    """Точное совпадение исходного строкового значения без нормализации."""

    column: str
    accepted_values: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> RowSelector:
        payload = as_config_object(raw, where)
        accepted = read_str_list(payload, 'values', where)
        if not accepted:
            raise ConfigValidationError(f'{where} → values: требуется непустой список уникальных строк')
        if len(set(accepted)) != len(accepted):
            raise ConfigValidationError(f'{where} → values: значения должны быть уникальны')
        return cls(column=read_text(payload, 'column', where), accepted_values=accepted)

    @classmethod
    def from_section(cls, section: RawConfig, where: str) -> RowSelector | None:
        if 'row_selector' not in section:
            return None
        return cls.from_dict(section.get('row_selector'), f'{where} → row_selector')

    def matches(self, fields: RawConfig) -> bool:
        cell = fields.get(self.column)
        return isinstance(cell, str) and bool(cell) and cell in self.accepted_values
