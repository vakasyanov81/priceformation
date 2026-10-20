"""Обёртка стратегии `title`: параметры позиции из названия (`title.params_from_title`)."""

from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache
from typing import Any, NamedTuple

from domain.row_item.row_item import RowItem
from parsers.strategies._disk_title_parser import DiskTitleParts, fill_disk_fields, parse_disk_title
from parsers.strategies._tire_title_parser import fill_tire_fields, parse_tire_title
from parsers.strategies._tube_title_parser import fill_tube_fields, parse_tube_title
from parsers.strategies.protocols import TitleStrategy
from parsers.strategies.title_conflicts import column_values, log_title_conflicts


class _Extractor(NamedTuple):
    """Разборщик названия одного вида позиции: разобрать и записать в поля."""

    parse: Callable[[str | None], Any]
    fill: Callable[[RowItem, Any], None]


def _fill_eet(row_item: RowItem, et_value: str) -> None:
    """Вылет из названия записать в поле: название главнее колонки."""
    row_item.set_field('eet', et_value)


def _parse_bare_disk(raw: str | None) -> DiskTitleParts | None:
    """Диск без слова «Диск» в начале (API Форточек): только с размером и крепежом."""
    return parse_disk_title(raw, bare=True)


# Разбор названия — чистая функция строки, а результаты неизменяемы (frozen dataclass / NamedTuple).
# Одно и то же название разбирается дважды: в enrich и в шаге `title` pipeline, поэтому кэш.
_PARSE_CACHE_SIZE = 65536
_tire = lru_cache(maxsize=_PARSE_CACHE_SIZE)(parse_tire_title)
_disk = lru_cache(maxsize=_PARSE_CACHE_SIZE)(parse_disk_title)
_bare_disk = lru_cache(maxsize=_PARSE_CACHE_SIZE)(_parse_bare_disk)
_eet = lru_cache(maxsize=_PARSE_CACHE_SIZE)(DiskTitleParts.et_from_name)
_tube = lru_cache(maxsize=_PARSE_CACHE_SIZE)(parse_tube_title)

# Каждый разборщик сам отвечает None на чужое название (диск — не шина и наоборот).
_EXTRACTORS = (
    _Extractor(_tire, fill_tire_fields),
    _Extractor(_disk, fill_disk_fields),
    _Extractor(_eet, _fill_eet),
    _Extractor(_tube, fill_tube_fields),
)
_BARE_EXTRACTORS = (
    _Extractor(_tire, fill_tire_fields),
    _Extractor(_bare_disk, fill_disk_fields),
    _Extractor(_eet, _fill_eet),
    _Extractor(_tube, fill_tube_fields),
)


def _fill_from_title(row_item: RowItem, title: str | None, extractors: tuple[_Extractor, ...]) -> None:
    """Записать в поля позиции параметры, которые разбираются из названия."""
    for extractor in extractors:
        parts = extractor.parse(title)
        if parts is not None:
            extractor.fill(row_item, parts)


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
        from_columns = column_values(row_item)
        _fill_from_title(row_item, title, _EXTRACTORS)
        log_title_conflicts(row_item, from_columns, title)
        return title


class ParamsBeforeTitle:
    """Разобрать исходное название в поля позиции, затем собрать название вложенной стратегией.

    Для поставщика, у которого название только в API: размер, индексы, камера, диск (без слова
    «Диск») берутся из исходного title, и сборка строит название по полям. Поля, уже заполненные
    колонками прайса, не перетираются (кроме индексов и вылета, где название главнее).
    """

    def __init__(self, inner: TitleStrategy) -> None:
        """Обернуть стратегию сборки названия."""
        self._inner = inner

    def prepare(self, row_item: RowItem) -> str | None:
        """Записать параметры из исходного title, затем вернуть собранное вложенной стратегией."""
        source_title = row_item.identity.title
        from_columns = column_values(row_item)
        _fill_from_title(row_item, source_title, _BARE_EXTRACTORS)
        log_title_conflicts(row_item, from_columns, source_title)
        return self._inner.prepare(row_item)
