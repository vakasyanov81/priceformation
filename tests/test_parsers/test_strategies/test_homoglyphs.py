"""Кириллические буквы-двойники: технические токены, слова и поля позиции."""

from __future__ import annotations

import logging

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies.homoglyph_tokens import fix_token
from parsers.strategies.homoglyphs import fix_row_homoglyphs, fix_text


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('TТ', 'TT'),
        ('ТT', 'TT'),
        ('ТТ', 'TT'),
        ('215/75R16С', '215/75R16C'),
        ('195R15С', '195R15C'),
        ('1200х500-508', '1200x500-508'),
        ('86Н', '86H'),
        ('102Н', '102H'),
        ('ЕТ35', 'ET35'),
        ('150/136A2/А6', '150/136A2/A6'),
        ('(TТ)', '(TT)'),
        ('Asimmetriсo', 'Asimmetrico'),
        ('Аveо', 'Aveo'),
        ('VС-1', 'VC-1'),
        ('СR-17', 'CR-17'),
        ('H108А', 'H108A'),
        ('H108С', 'H108C'),
        ('Е3/L3', 'E3/L3'),
        ('B-Р', 'B-P'),
    ],
)
def test_fix_token_replaces_doubles_with_latin(raw: str, expected: str) -> None:
    """Технические токены и смешанные части с преобладанием латиницы приводятся к латинице."""
    assert fix_token(raw) == (expected, False)


@pytest.mark.parametrize(
    'token',
    [
        'НК-241',
        'Кама-310',
        'О-79',
        'В-105А',
        'СВК',
        'КС1053',
        'Samara-оригинал',
        'Сахара-Patriot',
        '(Jac/Москвич',
        'SUNTOP+монтажный',
        'd=6.6мм',
        '16мм',
        'Н168',
    ],
)
def test_fix_token_keeps_single_alphabet_parts(token: str) -> None:
    """Части целиком в одном алфавите — русские модели и коды — не меняются."""
    assert fix_token(token) == (token, False)


def test_fix_token_reports_unfixable_mix() -> None:
    """`z` не имеет кириллической пары: смесь не исправляется, а возвращается как подозрительная."""
    word = 'Каzантип'

    assert fix_token(word) == (word, True)


def test_fix_text_keeps_spaces_and_collects_fixes() -> None:
    """Пробелы сохраняются; список содержит «было → стало» и подозрительные токены."""
    text, fixes = fix_text('195/75  R16С TТ Каzантип')

    assert text == '195/75  R16C TT Каzантип'
    assert fixes.fixed == [('R16С', 'R16C'), ('TТ', 'TT')]
    assert fixes.suspects == ['Каzантип']


def test_fix_row_homoglyphs_fixes_title_and_technical_fields(caplog: pytest.LogCaptureFixture) -> None:
    """Название и поля размера/индексов/камерности получают латиницу; исправление пишется в лог."""
    row = RowItem({'title': '215/75R16С Kama TТ', 'index_velocity': 'Н', 'layering': '8PR'})

    with caplog.at_level(logging.INFO):
        fixes = fix_row_homoglyphs(row)

    assert row.identity.title == '215/75R16C Kama TT'
    assert row.tire.index_velocity == 'H'
    assert row.tire.layering == '8PR'
    assert len(fixes.fixed) == 3
    assert 'исправлена' in caplog.text


def test_fix_row_homoglyphs_logs_suspects(caplog: pytest.LogCaptureFixture) -> None:
    """Подозрительный токен не меняется и попадает в лог предупреждением."""
    row = RowItem({'title': 'Каzантип'})

    with caplog.at_level(logging.WARNING):
        fixes = fix_row_homoglyphs(row)

    assert row.identity.title == 'Каzантип'
    assert fixes.suspects == ['Каzантип']
    assert 'не исправлено' in caplog.text
