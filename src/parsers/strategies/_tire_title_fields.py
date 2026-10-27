"""Бренд, модель и назначение из остатка токенов названия шины."""

from __future__ import annotations

import re
from typing import NamedTuple

from parsers.strategies._tire_title_tokens import take_token
from parsers.strategies._tire_title_usage import is_usage, trailing_paren_start

_PRODUCERS = frozenset(('НКШЗ', 'БШК', 'ОШЗ', 'ЯШЗ', 'ВОЛШЗ'))
# Заводской код без бренда: `ОИ-73Б`, `И-Н142Б`, `ВЛИ-10`, `Я-166`. До трёх заглавных букв —
# иначе под правило попали бы `КАМА-310` и `Алтайшина-421` (бренд со слитной моделью).
_FACTORY_CODE = re.compile(r'^[А-ЯЁ]{1,3}(?:-[А-ЯЁ])?-?\d+[А-ЯЁ]*$')


class TitleFields(NamedTuple):
    """Бренд, модель и назначение, выделенные из остатка токенов."""

    brand: str
    model: str
    usage: tuple[str, ...]


def resolve_fields(rest: tuple[str, ...]) -> TitleFields | None:
    """Бренд, модель и назначение из остатка; None без бренда с моделью."""
    if not rest:
        return None
    producer, tokens = take_token(list(rest), _is_producer)
    if not tokens:
        return None
    if not producer:
        return _without_producer(tokens)
    if _looks_like_brand(tokens[0]):
        fields = _compose_model(tokens[0], tokens[1:])
        return fields._replace(usage=(*fields.usage, producer))
    return _compose_model(producer, tokens)


def _without_producer(tokens: list[str]) -> TitleFields | None:
    """Бренд и модель, когда завода в хвосте нет; None, если первое слово — назначение (``об/лента``)."""
    if is_usage(tokens[0]):
        return None
    if _FACTORY_CODE.match(tokens[0]):
        return _compose_model('', tokens)
    return _compose_model(tokens[0], tokens[1:])


def _compose_model(brand: str, model_tokens: list[str]) -> TitleFields:
    """Бренд, модель и назначение по токенам модели (назначение — от первого маркера)."""
    usage_start = trailing_paren_start(model_tokens)
    for index, token in enumerate(model_tokens[:usage_start]):
        if is_usage(token):
            usage_start = index
            break
    model = ' '.join(model_tokens[:usage_start])
    return TitleFields(brand, model, tuple(model_tokens[usage_start:]))


def _looks_like_brand(token: str) -> bool:
    """Первый токен похож на бренд: латиница (``Tyrex``) или «кама» (``КАМА-310``)."""
    has_latin = any(char.isascii() and char.isalpha() for char in token)
    return has_latin or 'кама' in token.lower()


def _is_producer(token: str) -> bool:
    """Токен — завод-производитель из хвоста названия."""
    return token.upper() in _PRODUCERS
