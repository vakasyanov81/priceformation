"""tests for BaseFinder alias search."""

from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder


def test_find_uses_first_alias_occurrence() -> None:
    finder = BaseFinder(AliasContainer({"Brand": ()}))
    correct, found = finder.find_word_in_title("xx Brand yy BRAND zz")
    assert correct == "Brand"
    assert found == "Brand"


def test_find_title_equal_to_alias() -> None:
    finder = BaseFinder(AliasContainer({"НКШЗ": ()}))
    correct, found = finder.find_word_in_title("НКШЗ")
    assert correct == "НКШЗ"
    assert found == "НКШЗ"
