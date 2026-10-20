"""Стратегия слота `title` для Пошка и STK: сборка названия шины в каноническом порядке."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace

from domain.row_item.row_item import RowItem
from parsers.strategies._tire_title_parser import parse_tire_title
from parsers.strategies.protocols import BrandProbe
from parsers.strategies.title import NormalizeSizeChunks


class PoshkStkTireCompose:
    """Пошк/STK: разобрать параметры шины и склеить название в каноническом порядке.

    Порядок: ``размер бренд модель нагрузка/скорость PR камера ось``.
    Производитель из хвоста (``НКШЗ``/``БШК``/``ОШЗ``/``ЯШЗ``/``ВолШЗ``), если бренда в начале
    строки нет, становится брендом; канонический производитель позиции перекрывает
    разобранный бренд. Если строка не похожа на размер шины (например диск) или ведущая «Шина» не имеет бренда, работает
    обычная нормализация ``normalize_size_chunks``.

    Если камерности в названии нет, её даёт ``camera_by_kind``: слово вида шины
    в исходном названии (``автошина`` → ``TT``, ``автопокрышка`` → ``TL``).

    Примеры склейки — в ``_tire_title_parser``.
    """

    def __init__(
        self,
        fallback_brand: str,
        brand_probe: BrandProbe | None,
        camera_by_kind: Mapping[str, str] | None = None,
    ) -> None:
        """Запомнить бренд-заглушку, детектор бренда и карту камерности по виду; заготовить нормализацию."""
        self._camera_by_kind = camera_by_kind or {}
        self._fallback_brand = fallback_brand
        self._brand_probe = brand_probe
        self._fallback = NormalizeSizeChunks(fallback_brand, brand_probe)

    def prepare(self, row_item: RowItem) -> str | None:
        """Собрать название из разобранных параметров."""
        title = row_item.identity.title
        parts = parse_tire_title(title)
        if parts is None or self._ship_without_brand(title, parts.from_ship):
            return self._fallback.prepare(row_item)
        if not parts.intimacy:
            parts = replace(parts, intimacy=self._camera_for_kind(title))
        return parts.compose(row_item.identity.manufacturer)

    def _camera_for_kind(self, title: str | None) -> str:
        """Камерность по первому найденному слову вида шины; пусто, если слова нет."""
        lower = (title or '').lower()
        for kind, camera in self._camera_by_kind.items():
            if kind.lower() in lower:
                return camera.upper()
        return ''

    def _ship_without_brand(self, title: str | None, from_ship: bool) -> bool:
        """«Шина …» без бренда: вернуть нормализацию, чтобы подставился ``fallback_brand``."""
        if not from_ship or not self._fallback_brand or self._brand_probe is None:
            return False
        return not self._brand_probe(title)
