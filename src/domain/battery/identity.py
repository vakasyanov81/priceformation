"""Идентичность аккумулятора и адрес предложения поставщика."""

from collections.abc import Mapping
from dataclasses import dataclass

from domain.battery.conversions import text
from domain.battery.field_registry import read_field


@dataclass(frozen=True, slots=True)
class BatteryIdentity:
    """Название, производитель, линейка и коды; коды не определяют дубли."""

    title: str | None = None
    manufacturer_name: str | None = None
    model: str | None = None
    code: str | None = None
    code_art: str | None = None
    code_man: str | None = None

    @classmethod
    def from_fields(cls, fields: Mapping[str, object]) -> BatteryIdentity:
        """Прочитать только поля идентичности из проверенного входа."""
        return cls(
            title=read_field(fields, 'title', text),
            manufacturer_name=read_field(fields, 'manufacturer_name', text),
            model=read_field(fields, 'model', text),
            code=read_field(fields, 'code', text),
            code_art=read_field(fields, 'code_art', text),
            code_man=read_field(fields, 'code_man', text),
        )
