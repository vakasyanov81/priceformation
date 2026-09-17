"""Value Object: габариты шины."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TireDimensions:
    """Габаритные размеры шины."""

    width: str = ''
    height_percent: str = ''
    diameter: str = ''
    ext_diameter: int | float = 0

    @classmethod
    def from_flat(cls, store: dict[str, Any]) -> TireDimensions:
        """Собрать из плоского словаря (ключи — имена полей)."""
        return cls(
            width=store.get('width', ''),
            height_percent=store.get('height_percent', ''),
            diameter=store.get('diameter', ''),
            ext_diameter=store.get('ext_diameter', 0),
        )

    def to_flat(self) -> dict[str, Any]:
        """В плоский словарь."""
        return {
            'width': self.width,
            'height_percent': self.height_percent,
            'diameter': self.diameter,
            'ext_diameter': self.ext_diameter,
        }

    def __bool__(self) -> bool:
        """True если хотя бы одно поле заполнено."""
        return bool(self.width or self.height_percent or self.diameter or self.ext_diameter)
