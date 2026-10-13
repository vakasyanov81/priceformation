"""Нормализация названия для классификатора типа товара."""

from __future__ import annotations

import pytest

from parsers.strategies.normalize import NormalizeTitle, normalize_text, replace_homoglyphs


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('  Шина  ', 'шина'),
        ('ШИНА', 'шина'),
        ('Ободная\xa0лента', 'ободная лента'),
        ('205/55, R16', '205/55, r16'),
        ('12,5/80-18', '12.5/80-18'),
        ('205/55R16', '205/55r16'),
        ('a   b\tc', 'a b c'),
        (None, ''),
        ('', ''),
    ],
)
def test_normalize_text(raw: str | None, expected: str) -> None:
    """Регистр, неразрывный пробел, запятые в числах, одиночные пробелы."""
    assert normalize_text(raw) == expected


def test_normalize_text_keeps_keyword_lowercase_unfolded() -> None:
    """Гомоглифы не трогаются: русские ключевые слова остаются читаемыми."""
    assert normalize_text('Сельхозшина') == 'сельхозшина'


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('С', 'C'),
        ('с', 'c'),
        ('Р', 'P'),
        ('Х', 'X'),
        ('М', 'M'),
        ('Е', 'E'),
        ('О', 'O'),
        ('А', 'A'),
        ('В', 'B'),
        ('Т', 'T'),
        ('Н', 'H'),
        ('К', 'K'),
        ('205/55С16', '205/55C16'),
        ('33х12,5', '33x12,5'),
        ('ЕТ43', 'ET43'),
    ],
)
def test_replace_homoglyphs(raw: str, expected: str) -> None:
    """Кириллические гомоглифы заменяются на совпадающие латинские буквы."""
    assert replace_homoglyphs(raw) == expected


def test_normalize_title_strategy_is_unchanged() -> None:
    """Стратегия слота `title` не меняется: пробелы и десятичные запятые."""
    from domain.row_item.row_item import RowItem

    assert NormalizeTitle().prepare(RowItem({'title': '  12,5/80-18  Ободная '})) == '12.5/80-18 Ободная'
