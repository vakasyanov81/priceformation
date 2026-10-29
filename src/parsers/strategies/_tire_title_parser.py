"""Разбор и сборка названия шины (Пошк, STK, Пионер).

Пошк и STK пишут параметры шины вперемешку: ``н.с.N`` вместо ``NPR``, индекс
нагрузки/скорости стоит то до модели, то после неё, а производитель
(``НКШЗ``/``БШК``/``ОШЗ``/``ЯШЗ``/``ВолШЗ``) спрятан в хвосте названия,
а ``PR`` слипается с размером (``7.00 R16LT14PR``) или отрывается от числа
(``8 PR``). Разбираем название на параметры и собираем заново в каноническом порядке
(``nomenclature.title.TireTitleTokens``): ``размер бренд модель нагрузка/скорость PR камера ось``.
Из назначения в название идёт только ось из словаря (``Рулевая``/``Ведущая``/…), прочее (шип, завод,
``об/л``, ``спецшина``) в название не входит.

Примеры склейки → Пионер:

- ``10.00 R20 DOUBLEROAD DR-801 н.с.18 149/146K унив.ось с об/л автошина, шт``
  → ``10.00R20 DOUBLEROAD DR-801 149/146K 18PR Универсальная``
- ``11 R22.5 TAITONG HS103 н.с.16 146/143M вед.ось автопокрышка, (1 шт)``
  → ``11R22.5 TAITONG HS103 146/143M 16PR Ведущая``
- ``а/п 425/85R21 NORTEC TR-184-1 18PR 156J TT, шт``
  → ``425/85R21 NORTEC TR-184-1 156J 18PR TT``
- ``11.00 R20 И-68А н.с. 16 150/146K НКШЗ автошина, шт``
  → ``11.00R20 НКШЗ И-68А 150/146K 16PR`` — производитель из хвоста
  становится брендом (``НКШЗ → Кама`` подставит ``ManufacturerFinder``)
- ``12.4L-16 Бел-160М н.с.8 111A6 БШК сельхозшина, шт``
  → ``12.4L-16 БШК Бел-160М 111A6 8PR``
- ``17.5-25 Rockbuster H108A E3/L3 н.с.28 спецшина, шт``
  → ``17.5-25 Rockbuster H108A E3/L3 28PR``
- ``Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал`` (STK)
  → ``235/75R17.5 LingLong LLA78 143/141J 18PR TL``
- ``Автошина 7.00 R16LT14PR 118/114L GREENSTONE ST896 змейка`` (STK)
  → ``7.00R16LT GREENSTONE ST896 118/114L 14PR``
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from parsers.nomenclature.title import TireTitleTokens
from parsers.strategies._tire_size_parts import SizeParts, find_size
from parsers.strategies._tire_title_fields import resolve_fields
from parsers.strategies._tire_title_service import Service
from parsers.strategies._tire_title_tokens import clean_tokens, prepare_text, starts_with_ship
from parsers.strategies._tire_title_usage import axis

# Камера и ободная лента — не шина, их размер разбирает `_tube_title_parser`.
TUBE_PREFIX = re.compile(r'^\s*(?:авто)?камера\b|^\s*(?:ободная\s+)?лента\b', re.IGNORECASE)
# Альтернативная запись размера сразу за основным: `(1200x500-508)`, `/6.45-13`.
_ALT_SIZE = re.compile(r'^(?:\([^)]*\d[^)]*[x/\-][^)]*\)|/\d+(?:[.,]\d+)?-\d+(?:[.,]\d+)?)\s*')


@dataclass(frozen=True, slots=True)
class TireTitleParts:
    """Разобранные параметры названия Пошка/STK."""

    size: SizeParts
    brand: str
    model: str
    load: str
    velocity: str
    layering: str
    intimacy: str
    usage: tuple[str, ...]
    from_ship: bool = False
    xl: str = ''
    season_marks: tuple[str, ...] = ()

    @classmethod
    def from_raw(
        cls,
        size: SizeParts,
        tokens: list[str],
        from_ship: bool,
    ) -> TireTitleParts | None:
        """Собрать параметры из размера и остатка токенов; None без бренда с моделью."""
        service = Service.from_tokens(tokens)
        fields = resolve_fields(service.rest)
        if fields is None:
            return None
        return cls(
            size=size,
            brand=fields.brand,
            model=fields.model,
            load=service.load,
            velocity=service.velocity,
            layering=service.layering,
            intimacy=service.intimacy,
            usage=fields.usage,
            from_ship=from_ship,
            xl=service.xl,
            season_marks=service.season_marks,
        )

    @property
    def model_name(self) -> str:
        """Модель; у бренда со слитной моделью (``Кама-310``) — весь токен, он и есть название модели."""
        if self.model:
            return self.model
        return self.brand if any(char.isdigit() for char in self.brand) else ''

    @property
    def axis(self) -> str:
        """Ось из слов назначения (``вед.ось`` → ``ведущая``); пусто, если назначения нет."""
        return axis(self.usage)

    def size_with_alt(self) -> str:
        """Размер и альтернативная запись: ``/6.45-13`` клеится к размеру, ``(...)`` — через пробел."""
        size = self.size
        glue = '' if size.alt.startswith('/') else ' '
        return f'{size.label}{glue}{size.alt}'.strip()

    def compose(self, brand: str | None = None) -> str:
        """Склеить название в каноническом порядке; brand перекрывает разобранный.

        Из назначения в название идёт только ось из словаря; остальные слова (шип, завод, ``об/л``)
        отдельные поля или шум.
        """
        return TireTitleTokens(
            self.size_with_alt(),
            _canonical_brand(self.brand, brand),
            self.model,
            load_velocity=f'{self.load}{self.velocity}',
            xl=self.xl,
            layering=self.layering,
            camera=self.intimacy,
            season_marks=self.season_marks,
            axis=self.axis,
        ).compose()


def parse_tire_title(raw: str | None) -> TireTitleParts | None:
    """Разобрать название Пошка/STK на параметры; None, если это не размер шины."""
    if not raw or TUBE_PREFIX.match(raw):
        return None
    found = find_size(prepare_text(raw))
    if found is None:
        return None
    return _parts_after_size(raw, *found)


def _parts_after_size(raw: str, size_match: re.Match[str], head: str, tail: str) -> TireTitleParts | None:
    """Параметры по найденному размеру: срезать альтернативный размер, разобрать слова до и после."""
    alt = _ALT_SIZE.match(tail)
    if alt is not None:
        tail = tail[alt.end() :]
    if not tail or tail[0] in '(/':
        return None
    size = SizeParts.from_match(size_match, alt[0].strip() if alt else '')
    return TireTitleParts.from_raw(size, clean_tokens(f'{head} {tail}'), starts_with_ship(raw))


def _canonical_brand(parsed: str, canonical: str | None) -> str:
    """Канонический бренд вместо разобранного; приклеенную модель сохранить.

    ``GREENSTONE`` → ``GreenStone``, но ``Алтайшина-421``/``КАМА-310`` — бренд
    со слитной моделью: заменяется только начало, хвост ``-421`` остаётся.
    """
    if not canonical:
        return parsed
    if parsed.lower().startswith(canonical.lower()):
        return canonical + parsed[len(canonical) :]
    return canonical
