"""Корпус и обслуживание аккумулятора."""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from domain.battery.conversions import flag, number, text
from domain.battery.field_registry import read_field
from domain.battery.values import check_flag, check_number


@dataclass(frozen=True, slots=True)
class BatteryCase:
    """Габариты в мм; единица веса не выдумывается из отсутствующего заголовка."""

    length_mm: Decimal | None = None
    width_mm: Decimal | None = None
    height_mm: Decimal | None = None
    size_type: str | None = None
    bottom_mount: str | None = None
    serviceable: bool | None = None
    weight: Decimal | None = None

    def __post_init__(self) -> None:
        check_number(self.length_mm, 'length_mm')
        check_number(self.width_mm, 'width_mm')
        check_number(self.height_mm, 'height_mm')
        check_number(self.weight, 'weight')
        check_flag(self.serviceable, 'serviceable')

    @classmethod
    def from_fields(cls, fields: Mapping[str, object]) -> BatteryCase:
        """Прочитать корпус независимо от шинных размеров и реестров."""
        return cls(
            length_mm=read_field(fields, 'length_mm', number),
            width_mm=read_field(fields, 'width_mm', number),
            height_mm=read_field(fields, 'height_mm', number),
            size_type=read_field(fields, 'size_type', text),
            bottom_mount=read_field(fields, 'bottom_mount', text),
            serviceable=read_field(fields, 'serviceable', flag),
            weight=read_field(fields, 'weight', number),
        )
