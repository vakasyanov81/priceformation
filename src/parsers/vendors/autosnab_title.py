"""Разбор размера и модели из title Автоснабжения."""

import re
from typing import NamedTuple

from parsers.row_item.row_item import RowItem

_SIZE_PROFILE = re.compile(
    r"(?i)^(\d+(?:[.,]\d+)?)/(\d+(?:[.,]\d+)?)[z]?r(\d+(?:[.,]\d+)?)c?\b",
)
_SIZE_FLAT = re.compile(r"(?i)^(\d+(?:[.,]\d+)?)[z]?r(\d+(?:[.,]\d+)?)c?\b")
_SIZE_INCH = re.compile(r"(?i)^(\d{2,3})[xх](\d+(?:[.,]\d+)?)r(\d+(?:[.,]\d+)?)")
_LAYERING = re.compile(r"(?i)^\d+pr$")
_LOAD_SPEED = re.compile(r"(?i)^\d{2,3}(?:/\d{2,3})?[a-z]$")
_PAREN = re.compile(r"\([^)]*\)")
_STOP_WORDS = frozenset(
    (
        "tl",
        "tt",
        "ttf",
        "xl",
        "шип",
        "ведущая",
        "рулевая",
        "универсальная",
        "карьер",
        "прицеп",
        "руль",
        "ось",
        "m+s",
        "3pmsf",
    ),
)


class _ParsedSize(NamedTuple):
    width: str
    height: str
    diameter: str
    ext_diameter: str
    rest: str


def fill_from_title(row_item: RowItem) -> None:
    """Заполнить width/height/diameter/model из title. Без совпадения — не трогать."""
    parsed = _parse_size((row_item.title or "").strip())
    if parsed is None:
        return
    _apply_size(row_item, parsed)
    model = _model_from_rest(parsed.rest, row_item)
    if model and not row_item.model:
        row_item.model = model


def _parse_size(title: str) -> _ParsedSize | None:
    """Размер в начале title; иначе None."""

    def as_size(width: str, height: str, diameter: str, ext: str, end: int) -> _ParsedSize:
        return _ParsedSize(
            width.replace(",", "."),
            height.replace(",", "."),
            diameter.replace(",", "."),
            ext.replace(",", "."),
            title[end:],
        )

    matched = _SIZE_PROFILE.match(title)
    if matched is not None:
        width, height, diameter = matched.groups()
        return as_size(width, height, diameter, "", matched.end())
    matched = _SIZE_FLAT.match(title)
    if matched is not None:
        width, diameter = matched.groups()
        return as_size(width, "", diameter, "", matched.end())
    matched = _SIZE_INCH.match(title)
    if matched is None:
        return None
    ext_diameter, width, diameter = matched.groups()
    return as_size(width, "", diameter, ext_diameter, matched.end())


def _apply_size(row_item: RowItem, parsed: _ParsedSize) -> None:
    """Писать только пустые поля размера."""
    if not row_item.width:
        row_item.width = parsed.width
    if parsed.height and not row_item.height_percent:
        row_item.height_percent = parsed.height
    if not row_item.diameter:
        row_item.diameter = parsed.diameter
    if parsed.ext_diameter and not row_item.ext_diameter:
        row_item.ext_diameter = parsed.ext_diameter


def _model_from_rest(rest: str, row_item: RowItem) -> str:
    """Токены после размера и бренда до служебных (PR, индекс, ось)."""
    leftover = rest.strip()
    leftover = _lstrip_name(leftover, row_item.manufacturer)
    leftover = _lstrip_name(leftover, row_item.brand)
    leftover = _PAREN.sub(" ", leftover)
    tokens: list[str] = []
    for token in leftover.split():
        if _is_stop_token(token):
            break
        tokens.append(token)
    return " ".join(tokens)


def _lstrip_name(rest: str, name: str | None) -> str:
    """Убрать бренд в начале остатка, без частичных совпадений."""
    prefix = (name or "").strip()
    if not prefix:
        return rest
    lowered = rest.lower()
    if not lowered.startswith(prefix.lower()):
        return rest
    tail = rest[len(prefix) :]
    if tail and not tail[0].isspace():
        return rest
    return tail.lstrip()


def _is_stop_token(token: str) -> bool:
    lower = token.lower()
    if lower in _STOP_WORDS:
        return True
    if _LAYERING.match(token):
        return True
    return bool(_LOAD_SPEED.match(token))
