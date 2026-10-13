"""Обёртка стратегии `title`: поля позиции по маркерам исходного названия."""

from __future__ import annotations

from collections.abc import Mapping

from domain.row_item.row_item import RowItem
from parsers.strategies.protocols import TitleStrategy


class TitleWithMarkers:
    """Дописать поля позиции по подстрокам исходного названия (`title.markers`).

    Если название содержит маркер, незаполненные поля получают значения из
    конфига (Пошк: ``шип`` → ``season: зима``, ``spike: да``). Сравнение — без
    учёта регистра; уже заполненные поля не перетираются.
    """

    def __init__(self, inner: TitleStrategy, markers: Mapping[str, Mapping[str, str]]) -> None:
        """Обернуть стратегию картой маркеров названия."""
        self._inner = inner
        self._markers = markers

    def prepare(self, row_item: RowItem) -> str | None:
        """Проставить поля по маркерам исходного названия и подготовить title."""
        self._apply_markers(row_item)
        return self._inner.prepare(row_item)

    def _apply_markers(self, row_item: RowItem) -> None:
        title = (row_item.identity.title or '').lower()
        for marker, fields in self._markers.items():
            if marker.lower() not in title:
                continue
            for key, field_value in fields.items():
                if not row_item.get_field(key):
                    row_item.set_field(key, field_value)
