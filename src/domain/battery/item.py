"""Позиция аккумулятора: отдельные типизированные характеристики и предложение."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from domain.battery.case import BatteryCase
from domain.battery.field_registry import validate_fields
from domain.battery.identity import BatteryIdentity
from domain.battery.offer import BatteryOffer
from domain.battery.parameters import BatteryParameters
from domain.product_groups import ProductGroup


@dataclass(frozen=True, slots=True)
class BatteryItem:
    """Неизменяемая аккумуляторная позиция без шинных полей и ввода-вывода."""

    identity: BatteryIdentity = field(default_factory=BatteryIdentity)
    electrical: BatteryParameters = field(default_factory=BatteryParameters)
    case: BatteryCase = field(default_factory=BatteryCase)
    offer: BatteryOffer = field(default_factory=BatteryOffer)

    @property
    def product_group(self) -> Literal[ProductGroup.BATTERIES]:
        """Принадлежность модели нельзя передать отдельным аргументом."""
        return ProductGroup.BATTERIES

    @classmethod
    def from_fields(cls, fields: Mapping[str, object]) -> BatteryItem:
        """Создать позицию из отображённых колонок с проверкой чужих полей."""
        validate_fields(fields)
        return cls(
            identity=BatteryIdentity.from_fields(fields),
            electrical=BatteryParameters.from_fields(fields),
            case=BatteryCase.from_fields(fields),
            offer=BatteryOffer.from_fields(fields),
        )
