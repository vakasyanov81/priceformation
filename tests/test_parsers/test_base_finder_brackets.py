"""Поиск производителя: текст в скобках (владелец бренда) не перебивает слово перед ними."""

from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder, blank_brackets


def _finder() -> BaseFinder:
    return BaseFinder(AliasContainer({'Bridgestone': 'bridgestone', 'Gislaved': 'gislaved'}))


def test_blank_brackets_keeps_length() -> None:
    assert blank_brackets('A (B) C') == 'A     C'


def test_manufacturer_before_brackets_wins() -> None:
    assert _finder().find_word_in_title('175/70R13 Gislaved (Bridgestone) SpikeControl 82T')[0] == 'Gislaved'


def test_manufacturer_only_in_brackets_is_still_found() -> None:
    assert _finder().find_word_in_title('175/70R13 Foo (Bridgestone) Bar 82T')[0] == 'Bridgestone'
