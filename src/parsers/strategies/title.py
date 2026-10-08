"""
Стратегии слота `title`: подготовка названия строки.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from typing import ClassVar

from domain.row_item.row_item import RowItem
from parsers.nomenclature_title import (
    brand_label,
    compose_tire_title,
    join_size_parts,
    join_title_parts,
    load_velocity,
)
from parsers.strategies._autosnab_helper import fill_from_title
from parsers.strategies._four_tochki_disk_helper import (
    disk_diameter,
    disk_name_suffix,
    et_label,
    fill_disk_thickness,
)
from parsers.strategies._four_tochki_tire_helper import get_prepared_title as compose_four_tochki
from parsers.strategies.protocols import TitleStrategy

_SIZE_MARK = 'x'


class DefaultTitle:
    """Оставить title без изменений."""

    def prepare(self, row_item: RowItem) -> str | None:
        """Исходный title строки."""
        return row_item.identity.title


class NormalizeSizeChunks:
    """Пошк: срезать обёртки «Шина»/«а/п»/«автошина»/«автопокрышка»/«, шт», `*`→`x`, «н.с.N»→«PRN»."""

    _PART_SIZE = re.compile(r'^\d+\.*\d*')
    _R_DIAMETER = re.compile(r'R\d+.')
    _COMMA = re.compile(r'(\d),(\d)')
    _LEADING_SHIP = re.compile(r'^\s*Шина\b\s*', re.IGNORECASE)
    _TRAILING_PIECE = re.compile(r'\s*,\s*,?\s*шт\s*$', re.IGNORECASE)
    _DROP_WORD = re.compile(r'\s*,?\s*(?:а/п|автошина|автопокрышка)\b\s*,?', re.IGNORECASE)
    _LAYER_NORM = re.compile(r'н\.\s*с\.?\s*(\d+)', re.IGNORECASE)

    def prepare(self, row_item: RowItem) -> str | None:
        """Нормализовать title по правилам Пошка."""
        title = self._trim_wrappers(row_item.identity.title or '')
        chunks = [chunk.strip() for chunk in title.split() if chunk.strip()]
        normalized = self._COMMA.sub(r'\1.\2', ' '.join(self._normalize_chunks(chunks)))
        return self._LAYER_NORM.sub(r'PR\1', normalized)

    def _trim_wrappers(self, title: str) -> str:
        title = self._LEADING_SHIP.sub('', title)
        title = self._TRAILING_PIECE.sub('', title)
        return self._DROP_WORD.sub(' ', title).strip()

    def _normalize_chunks(self, chunks: list[str]) -> list[str]:
        for index, chunk in enumerate(chunks):
            if '*' in chunk and self._PART_SIZE.match(chunk):
                chunks[index] = chunk.replace('*', _SIZE_MARK)
        if len(chunks) > 1 and self._R_DIAMETER.match(chunks[1]):
            chunks[0] += chunks.pop(1)
        return chunks


class TireCompose:
    """Сборка title шины; вариант задаёт набор полей."""

    _MIM_SIMPLE = 'mim_simple'
    _MIM_TRUCK = 'mim_truck'

    def __init__(self, variant: str) -> None:
        """Запомнить вариант сборки."""
        self._variant = variant

    def prepare(self, row_item: RowItem) -> str | None:
        """Собрать title выбранным вариантом."""
        if self._variant == self._MIM_SIMPLE:
            return self._mim_simple(row_item)
        if self._variant == self._MIM_TRUCK:
            return self._mim_truck(row_item)
        return compose_four_tochki(row_item)

    def _mim_simple(self, row_item: RowItem) -> str:
        profile = row_item.tire.height_percent or ''
        delimiter = _SIZE_MARK if self._is_decimal(profile) else '/'
        size = join_size_parts(row_item.tire.width, delimiter, profile, 'R', row_item.tire.diameter)
        return compose_tire_title(row_item, size, load_velocity(row_item))

    def _mim_truck(self, row_item: RowItem) -> str:
        height_percent = row_item.tire.height_percent or ''
        diameter = row_item.tire.diameter or ''
        profile = f'/{height_percent}' if height_percent else ''
        size = join_size_parts(row_item.tire.width, profile, f'R{diameter}' if diameter else '')
        return compose_tire_title(
            row_item,
            size,
            row_item.tire.layering,
            load_velocity(row_item),
            row_item.tire.intimacy,
            row_item.tire.axis,
        )

    def _is_decimal(self, candidate: str | int | float) -> bool:
        try:
            return bool(float(candidate)) and '.' in str(candidate)
        except ValueError:
            return False


class DiskComposeTochki:
    """Сборка title диска Форточек."""

    def prepare(self, row_item: RowItem) -> str | None:
        """Собрать title диска с хвостом из исходного наименования."""
        original_name = row_item.identity.title or ''
        fill_disk_thickness(row_item)
        return join_title_parts(self._disk_title(row_item), disk_name_suffix(original_name))

    def _disk_title(self, row_item: RowItem) -> str:
        return join_title_parts(
            join_size_parts(row_item.tire.width, _SIZE_MARK, disk_diameter(row_item.tire.diameter)),
            join_size_parts(row_item.disk.slot_count, _SIZE_MARK, row_item.disk.pcd1),
            et_label(row_item.disk.eet),
            row_item.disk.central_diameter,
            row_item.disk.color,
            brand_label(row_item),
            row_item.identity.model,
        )


class FillFieldsFromTitle:
    """Автоснабжение: дописать поля размера и модели из title."""

    def prepare(self, row_item: RowItem) -> str | None:
        """Разобрать размер из title; сам title не меняется."""
        fill_from_title(row_item)
        return row_item.identity.title


class ManufacturerFromCategory:
    """Производитель из раздела-категории: в brand и, при закупе, в title."""

    _MANUFACTURER_MAP: ClassVar[Mapping[str, str]] = {'рокбастер': 'RockBuster'}

    def __init__(self, manufacturer_reader: Callable[[], str | None]) -> None:
        """Запомнить читателя производителя текущего раздела."""
        self._manufacturer_reader = manufacturer_reader

    def prepare(self, row_item: RowItem) -> str | None:
        """Записать brand и, при наличии закупа, вставить производителя в title."""
        manufacturer = self._manufacturer_reader()
        row_item.set_field('brand', manufacturer)
        if manufacturer and row_item.pricing.price_opt:
            self._prepend_manufacturer(row_item, manufacturer)
        return row_item.identity.title

    def _prepend_manufacturer(self, row_item: RowItem, manufacturer: str) -> None:
        display_name = self._MANUFACTURER_MAP.get(manufacturer, manufacturer)
        title = row_item.identity.title
        if title is None or display_name.lower() in title.lower():
            return
        chunks = title.split(' ')
        chunks[0] = f'{chunks[0]} {display_name}'
        row_item.set_field('title', ' '.join(chunks))


class TitleWithAliases:
    """Заменить подготовленный title по таблице title_aliases.json."""

    def __init__(self, inner: TitleStrategy, aliases: Mapping[str, str]) -> None:
        """Обернуть стратегию таблицей синонимов."""
        self._inner = inner
        self._aliases = aliases

    def prepare(self, row_item: RowItem) -> str | None:
        """Сначала подготовить title вложенной стратегией, затем заменить по таблице."""
        title = self._inner.prepare(row_item)
        if title is None:
            return None
        return self._aliases.get(title) or title
