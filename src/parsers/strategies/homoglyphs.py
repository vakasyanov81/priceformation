"""Кириллические буквы-двойники в названии и технических полях позиции.

Поставщики набирают `TТ`, `R16С`, `86Н`, `ЕТ35`, где одна из букв кириллическая. Правила по токенам —
в `homoglyph_tokens.py`; здесь — применение к строке и к позиции с записью в лог (только файл).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from domain.row_item.row_item import RowItem
from infrastructure.logging.console import FILE_ONLY
from parsers.strategies.homoglyph_alphabet import LATIN, convert
from parsers.strategies.homoglyph_tokens import fix_token

logger = logging.getLogger(__name__)

_TOKEN = re.compile(r'\S+')
# Поля, где допустима только латиница.
TECHNICAL_FIELDS = (
    'width',
    'height_percent',
    'diameter',
    'index_load',
    'index_velocity',
    'layering',
    'intimacy',
)


@dataclass
class HomoglyphFix:
    """Итог разбора: пары «было → стало» и токены со смесью алфавитов, оставленные как есть."""

    fixed: list[tuple[str, str]] = field(default_factory=list)
    suspects: list[str] = field(default_factory=list)


def fix_text(text: str) -> tuple[str, HomoglyphFix]:
    """Исправить двойники во всех токенах строки; пробелы сохраняются."""
    fixes = HomoglyphFix()

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        fixed, unresolved = fix_token(token)
        if fixed != token:
            fixes.fixed.append((token, fixed))
        elif unresolved:
            fixes.suspects.append(token)
        return fixed

    return _TOKEN.sub(replace, text), fixes


def _fix_fields(row_item: RowItem, fixes: HomoglyphFix) -> None:
    for key in TECHNICAL_FIELDS:
        raw = row_item.get_field(key)
        if isinstance(raw, str) and convert(raw, LATIN) != raw:
            fixes.fixed.append((raw, convert(raw, LATIN)))
            row_item.set_field(key, convert(raw, LATIN))


def _log_fixes(title: str | None, fixes: HomoglyphFix) -> None:
    for before, after in fixes.fixed:
        logger.info(f'Кириллическая буква-двойник исправлена: {before!r} → {after!r}', extra={FILE_ONLY: True})
    for word in fixes.suspects:
        logger.warning(f'Смесь латиницы и кириллицы, не исправлено: {word!r} // {title}', extra={FILE_ONLY: True})


def fix_row_homoglyphs(row_item: RowItem) -> HomoglyphFix:
    """Исправить двойники в названии и технических полях позиции."""
    title = row_item.identity.title
    fixed_title, fixes = fix_text(title or '')
    if title and fixed_title != title:
        row_item.set_field('title', fixed_title)
    _fix_fields(row_item, fixes)
    _log_fixes(title, fixes)
    return fixes
