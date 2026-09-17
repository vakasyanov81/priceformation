"""Value Object: параметры диска."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DiskParameters:
    """Параметры колёсного диска."""

    slot_count: int = 0
    pcd1: int | float = 0
    pcd2: int = 0
    eet: int | float = 0
    central_diameter: int | float = 0
    disk_thickness: str = ''

    @classmethod
    def from_flat(cls, store: dict[str, Any]) -> DiskParameters:
        """Собрать из плоского словаря."""
        return cls(
            slot_count=store.get('slot_count', 0),
            pcd1=store.get('pcd1', 0),
            pcd2=store.get('pcd2', 0),
            eet=store.get('eet', 0),
            central_diameter=store.get('central_diameter', 0),
            disk_thickness=store.get('disk_thickness', ''),
        )

    def to_flat(self) -> dict[str, Any]:
        """В плоский словарь."""
        return {
            'slot_count': self.slot_count,
            'pcd1': self.pcd1,
            'pcd2': self.pcd2,
            'eet': self.eet,
            'central_diameter': self.central_diameter,
            'disk_thickness': self.disk_thickness,
        }

    def __bool__(self) -> bool:
        """True если хотя бы одно поле заполнено."""
        has_hub = bool(self.slot_count or self.pcd1 or self.pcd2)
        has_rim = bool(self.eet or self.central_diameter or self.disk_thickness)
        return has_hub or has_rim
