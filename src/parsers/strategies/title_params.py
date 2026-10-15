"""Обёртка стратегии `title`: параметры позиции из названия (`title.params_from_title`)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, NamedTuple

from domain.row_item.row_item import RowItem
from parsers.strategies._disk_title_parser import fill_disk_fields, parse_disk_title
from parsers.strategies._tire_title_parser import fill_tire_fields, parse_tire_title
from parsers.strategies._tube_title_parser import fill_tube_fields, parse_tube_title
from parsers.strategies.protocols import TitleStrategy


class _Extractor(NamedTuple):
    """Разборщик названия одного вида позиции: разобрать и записать в поля."""

    parse: Callable[[str | None], Any]
    fill: Callable[[RowItem, Any], None]


# Каждый разборщик сам отвечает None на чужое название (диск — не шина и наоборот).
_EXTRACTORS = (
    _Extractor(parse_tire_title, fill_tire_fields),
    _Extractor(parse_disk_title, fill_disk_fields),
    _Extractor(parse_tube_title, fill_tube_fields),
)


class ParamsFromTitle:
    """Достать параметры шин, дисков и т.п. из подготовленного названия в поля позиции.

    Название готовит вложенная стратегия, затем все разборщики пробуют его разобрать;
    поля, уже заполненные из колонок прайса, не перетираются, название не меняется.
    """

    def __init__(self, inner: TitleStrategy) -> None:
        """Обернуть стратегию разбором параметров."""
        self._inner = inner

    def prepare(self, row_item: RowItem) -> str | None:
        """Подготовить title вложенной стратегией и записать параметры из него."""
        title = self._inner.prepare(row_item)
        for extractor in _EXTRACTORS:
            parts = extractor.parse(title)
            if parts is not None:
                extractor.fill(row_item, parts)
        return title
