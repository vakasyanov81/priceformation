"""Поиск производителя: текст в скобках (владелец бренда) не перебивает слово перед ними."""

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
