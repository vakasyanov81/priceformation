"""Исправление кириллических двойников в одном токене.

Технические токены (размер, нагрузка и скорость, слойность, камерность, `XL`, `ET`) приводятся
к латинице целиком. В остальных токенах часть между разделителями приводится к алфавиту, который
в ней подтверждён буквами без двойника или, если таких нет, преобладает. Что определить нельзя
(`Каzантип`), не меняется, а возвращается как подозрительное.
"""

from __future__ import annotations

import re
from typing import Final

from parsers.strategies.homoglyph_alphabet import DOUBLE_CYRILLIC, LATIN, convert
from parsers.strategies.homoglyph_parts import fix_part, is_latin_part

_NUM: Final = r'\d+(?:[.,]\d+)?'
_TECHNICAL: Final = re.compile(
    '|'.join(
        (
            rf'{_NUM}(?:/{_NUM})?(?:ZR|R|-){_NUM}(?:[Cc]|LT|CP)?',  # 215/75R16C, 10.00-20
            rf'{_NUM}[xX]{_NUM}(?:[-R]{_NUM})?(?:[Cc]|LT)?',  # 31X10.50R15LT, 1200x500-508
            r'\d{2,3}(?:/\d{2,3})?[A-Z]\d?(?:/[A-Z]\d)?',  # 86H, 154/150L, 150/136A2/A6
            r'[A-Z]\d(?:/[A-Z]\d)+',  # E3/L3
            r'\d{1,2}PR|PR\d{1,2}|TT|TTF|TL|XL|RF|M\+S|3PMSF|ET-?\d+(?:[.,]\d+)?',
        ),
    ),
)
_SEPARATORS: Final = re.compile(r'([-/+()=])')
_WRAPPED: Final = re.compile(r'([(\[]*)(.*?)([)\],;.]*)', re.DOTALL)


def _fix_word(word: str) -> tuple[str, bool]:
    """Исправить слово по разделителям; True во втором элементе — часть определить не удалось."""
    parts = _SEPARATORS.split(word)
    latin_sibling = len(parts) > 1 and any(map(is_latin_part, parts))
    fixed = [fix_part(part, latin_sibling=latin_sibling) for part in parts]
    texts, flags = zip(*fixed, strict=True)
    return ''.join(texts), any(flags)


def _unwrap(token: str) -> tuple[str, str, str]:
    """Скобки и знаки препинания вокруг токена: (начало, ядро, конец)."""
    wrapped = _WRAPPED.fullmatch(token)
    if wrapped is None:
        return '', token, ''
    return wrapped[1], wrapped[2], wrapped[3]


def _fix_core(core: str) -> tuple[str, bool]:
    """Технический токен целиком в латиницу, иначе правило слов."""
    latin = convert(core, LATIN)
    if _TECHNICAL.fullmatch(latin):
        return latin, False
    return _fix_word(core)


def fix_token(token: str) -> tuple[str, bool]:
    """Исправить один токен; второй элемент — True, если смесь алфавитов исправить нельзя."""
    head, core, tail = _unwrap(token)
    if not any(char in DOUBLE_CYRILLIC for char in core):
        return token, False
    fixed, unresolved = _fix_core(core)
    return f'{head}{fixed}{tail}', unresolved
