"""Модели схемы прайса."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

type Columns = Mapping[int | str, str]
type HeadRows = tuple[tuple[Any, ...], ...]


@dataclass(frozen=True, slots=True)
class SheetHead:
    """Вкладка прайса: название и первые строки (шапка)."""

    name: str
    rows: HeadRows


@dataclass(frozen=True, slots=True)
class FileHead:
    """Прочитанное из файла прайса для построения схемы: вкладки xls(x) или ключи записей json."""

    sheets: tuple[SheetHead, ...] = ()
    json_keys: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class SheetSchema:
    """Вкладка секции: название и заголовок каждой используемой колонки (колонки без заголовка не входят)."""

    name: str
    headers: dict[int, str]


@dataclass(frozen=True, slots=True)
class PriceSchema:
    """Схема файла для секции поставщика: вкладки по индексу либо присутствующие json-ключи."""

    sheets: dict[int, SheetSchema]
    json_keys: frozenset[str]
