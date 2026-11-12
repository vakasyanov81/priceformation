"""Электрические характеристики и подключение аккумулятора."""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from domain.battery.conversions import flag, number, text
from domain.battery.field_registry import read_field
from domain.battery.values import check_flag, check_number


@dataclass(frozen=True, slots=True)
class BatteryParameters:
    """Ёмкость и ток с явными единицами; технология и полярность независимы."""

    capacity_ah: Decimal | None = None
    starting_current_a: Decimal | None = None
    current_standard: str | None = None
    terminal_type: str | None = None
    polarity: str | None = None
    efb: bool | None = None
    agm: bool | None = None

    def __post_init__(self) -> None:
        check_number(self.capacity_ah, 'capacity_ah')
        check_number(self.starting_current_a, 'starting_current_a')
        check_flag(self.efb, 'efb')
        check_flag(self.agm, 'agm')

    @classmethod
    def from_fields(cls, fields: Mapping[str, object]) -> BatteryParameters:
        """Неизвестная технология остаётся None, а не превращается в обычную АКБ."""
        return cls(
            capacity_ah=read_field(fields, 'capacity_ah', number),
            starting_current_a=read_field(fields, 'starting_current_a', number),
            current_standard=read_field(fields, 'current_standard', text),
            terminal_type=read_field(fields, 'terminal_type', text),
            polarity=read_field(fields, 'polarity', text),
            efb=read_field(fields, 'efb', flag),
            agm=read_field(fields, 'agm', flag),
        )
