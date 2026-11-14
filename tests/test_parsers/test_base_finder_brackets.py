"""Поиск производителя: текст в скобках (владелец бренда) не перебивает слово перед ними."""

import pytest

from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.alias_search import blank_brackets
from parsers.base_parser.base_finder import BaseFinder


def _finder() -> BaseFinder:
    return BaseFinder(AliasContainer({'Bridgestone': 'bridgestone', 'Gislaved': 'gislaved'}))


def test_blank_brackets_keeps_length() -> None:
    assert blank_brackets('A (B) C') == 'A     C'


def test_manufacturer_before_brackets_wins() -> None:
    assert _finder().find_word_in_title('175/70R13 Gislaved (Bridgestone) SpikeControl 82T')[0] == 'Gislaved'


def test_manufacturer_only_in_brackets_is_still_found() -> None:
    assert _finder().find_word_in_title('175/70R13 Foo (Bridgestone) Bar 82T')[0] == 'Bridgestone'


def test_brackets_inside_alias_are_kept() -> None:
    finder = BaseFinder(AliasContainer({'Ikon Tyres': ('ikon (nokian tyres)',), 'Nokian': ('nokian tyres',)}))

    assert finder.find_word_in_title('255/35R19 Ikon (Nokian Tyres) Autograph Ice 9 96T')[0] == 'Ikon Tyres'


@pytest.mark.parametrize('prefix', ['', ' ', '255/35R19 '])
def test_bracket_alias_preserves_exact_supplier_spelling(prefix: str) -> None:
    """Производитель и исходный алиас возвращаются целиком при любом смещении."""
    finder = BaseFinder(AliasContainer({'Ikon Tyres': ('ikon (nokian tyres)',)}))
    assert finder.find_word_in_title(f'{prefix}IKON (Nokian Tyres) Ice 9') == (
        'Ikon Tyres',
        'IKON (Nokian Tyres)',
    )


def test_absent_bracket_alias_allows_regular_manufacturer() -> None:
    """Отсутствующий составной алиас не прерывает обычный поиск производителя."""
    finder = BaseFinder(AliasContainer({'Ikon Tyres': ('ikon (nokian tyres)',), 'Nortec': ()}))
    assert finder.find_word_in_title('Nortec (Russia) 175R16') == ('Nortec', 'Nortec')


def test_unbounded_alias_allows_next_manufacturer() -> None:
    """Вхождение первого бренда внутрь слова не мешает найти следующий бренд."""
    finder = BaseFinder(AliasContainer({'Bridgestone': (), 'Nortec': ()}))
    assert finder.find_word_in_title('Bridgestoneish Nortec 175R16') == ('Nortec', 'Nortec')
