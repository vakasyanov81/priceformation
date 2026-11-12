"""Исходные строки прайса до отображения колонок в поля доменной модели."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RawRow:
    """Исходные значения строки и её физический номер, начиная с единицы."""

    fields: dict[str, Any]
    row_number: int


@dataclass(frozen=True, slots=True)
class RawTable:
    """Один лист XLSX либо входной массив JSON без листа."""

    sheet_index: int | None
    rows: tuple[RawRow, ...]
