"""Стратегия слота `title` для Пошка: сборка названия шины в порядке Пионера."""

from __future__ import annotations

from domain.row_item.row_item import RowItem
from parsers.strategies._poshk_title_helper import fill_poshk_fields, parse_poshk_title
from parsers.strategies.protocols import BrandProbe
from parsers.strategies.title import NormalizeSizeChunks


class PoshkTireCompose:
    """Пошк: разобрать параметры шины и склеить название в порядке Пионера.

    Порядок Пионера: ``размер бренд модель нагрузка/скорость PR камера
    назначение``. Производитель из хвоста (``НКШЗ``/``БШК``/``ОШЗ``/``ЯШЗ``/
    ``ВолШЗ``), если бренда в начале строки нет, становится брендом. Если строка
    не похожа на размер шины (например диск) или ведущая «Шина» не имеет бренда,
    работает обычная нормализация ``normalize_size_chunks``.

    Примеры склейки — в ``_poshk_title_helper``.
    """

    def __init__(self, fallback_brand: str = '', brand_probe: BrandProbe | None = None) -> None:
        """Запомнить бренд-заглушку и детектор бренда; заготовить нормализацию."""
        self._fallback_brand = fallback_brand
        self._brand_probe = brand_probe
        self._fallback = NormalizeSizeChunks(fallback_brand, brand_probe)

    def prepare(self, row_item: RowItem) -> str | None:
        """Собрать название Пошка из разобранных параметров."""
        title = row_item.identity.title or ''
        parts = parse_poshk_title(title)
        if parts is None or self._ship_without_brand(title, parts.from_ship):
            return self._fallback.prepare(row_item)
        fill_poshk_fields(row_item, parts)
        return parts.compose()

    def _ship_without_brand(self, title: str, from_ship: bool) -> bool:
        """«Шина …» без бренда: вернуть нормализацию, чтобы подставился ``fallback_brand``."""
        if not from_ship or not self._fallback_brand or self._brand_probe is None:
            return False
        return not self._brand_probe(title)
