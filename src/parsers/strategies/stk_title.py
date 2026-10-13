"""Стратегия слота `title` для STK: сборка названия шины в порядке Пионера."""

from __future__ import annotations

from domain.row_item.row_item import RowItem
from parsers.strategies._stk_title_helper import fill_stk_fields, parse_stk_title
from parsers.strategies.title import NormalizeSizeChunks


class StkTireCompose:
    """STK: разобрать параметры шины и склеить название в порядке Пионера.

    Порядок Пионера: ``размер бренд модель нагрузка/скорость PR камера
    назначение``. Если строка не похожа на размер шины (например диск),
    работает обычная нормализация ``normalize_size_chunks``.

    Примеры склейки — в ``_stk_title_helper``.
    """

    def __init__(self) -> None:
        """Заготовить нормализацию для строк без размера шины."""
        self._fallback = NormalizeSizeChunks()

    def prepare(self, row_item: RowItem) -> str | None:
        """Собрать название STK из разобранных параметров."""
        parts = parse_stk_title(row_item.identity.title or '')
        if parts is None:
            return self._fallback.prepare(row_item)
        fill_stk_fields(row_item, parts)
        return parts.compose(row_item.identity.manufacturer)
