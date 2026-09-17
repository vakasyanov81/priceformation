"""Value Object: информация о дублировании позиции."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DuplicateInfo:
    """Служебные поля группировки и дублей."""

    order: int = 0
    group_by_params: int = 0
    is_double: bool = False
    double_candidate: bool = False
    disputed: str = ''

    @classmethod
    def from_flat(cls, store: dict[str, Any]) -> DuplicateInfo:
        """Собрать из плоского словаря."""
        return cls(
            order=store.get('order', 0),
            group_by_params=store.get('group_by_params', 0),
            is_double=store.get('is_double', False),
            double_candidate=store.get('double_candidate', False),
            disputed=store.get('disputed', ''),
        )

    def to_flat(self) -> dict[str, Any]:
        """В плоский словарь."""
        return {
            'order': self.order,
            'group_by_params': self.group_by_params,
            'is_double': self.is_double,
            'double_candidate': self.double_candidate,
            'disputed': self.disputed,
        }
