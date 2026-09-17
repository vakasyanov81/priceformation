"""Value Object: идентификация товара (бренд, модель, коды)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProductIdentity:
    """Производитель, бренд, модель товара."""

    manufacturer: str = ''
    brand: str = ''
    model: str = ''
    codes: list[str] = field(default_factory=list)

    @classmethod
    def from_flat(cls, store: dict[str, Any]) -> ProductIdentity:
        """Собрать из плоского словаря.
        Внутренний ключ manufacturer_name (FieldDescriptor), атрибут — manufacturer.
        """
        return cls(
            manufacturer=store.get('manufacturer_name', store.get('manufacturer', '')),
            brand=store.get('brand', ''),
            model=store.get('model', ''),
        )

    def to_flat(self) -> dict[str, Any]:
        """В плоский словарь."""
        return {
            'manufacturer_name': self.manufacturer,
            'brand': self.brand,
            'model': self.model,
        }
