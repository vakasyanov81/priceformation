"""tests for BaseFinder alias search."""

from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder


def test_find_uses_first_alias_occurrence() -> None:
    finder = BaseFinder(AliasContainer({'Brand': ()}))
    correct, found = finder.find_word_in_title('xx Brand yy BRAND zz')
    assert correct == 'Brand'
    assert found == 'Brand'


def test_find_title_equal_to_alias() -> None:
    finder = BaseFinder(AliasContainer({'НКШЗ': ()}))
    correct, found = finder.find_word_in_title('НКШЗ')
    assert correct == 'НКШЗ'
    assert found == 'НКШЗ'


def test_find_alias_at_start_of_title() -> None:
    """Алиас в начале title (без пробела слева)."""
    finder = BaseFinder(AliasContainer({'НКШЗ': ()}))
    correct, found = finder.find_word_in_title('НКШЗ 175R16')
    assert correct == 'НКШЗ'
    assert found == 'НКШЗ'


def test_find_alias_at_end_of_title() -> None:
    """Алиас в конце title (без пробела справа)."""
    finder = BaseFinder(AliasContainer({'Bridgestone': ()}))
    correct, found = finder.find_word_in_title('шина Bridgestone')
    assert correct == 'Bridgestone'
    assert found == 'Bridgestone'


def test_title_lower_none_before_find() -> None:
    """title_lower = None при невызванном find_word_in_title."""
    finder = BaseFinder(AliasContainer({'A': ()}))
    assert finder.title_lower is None


def test_find_with_empty_title_returns_none() -> None:
    """Пустой title — ничего не найдено."""
    finder = BaseFinder(AliasContainer({'A': ()}))
    correct, found = finder.find_word_in_title('')
    assert correct is None
    assert found is None


def test_find_alias_no_whitespace_wrap() -> None:
    """Алиас без пробелов внутри слова не находится."""
    finder = BaseFinder(AliasContainer({'B': ()}))
    correct, found = finder.find_word_in_title('ABC')
    assert correct is None
    assert found is None


def test_find_alias_glued_with_hyphen() -> None:
    """Бренд через дефис находится: NORTEC-16 → Nortec."""
    finder = BaseFinder(AliasContainer({'Nortec': ()}))
    correct, found = finder.find_word_in_title('Диск штамп nortec-16 11.75x22.5')
    assert correct == 'Nortec'
    assert found == 'nortec'


def test_find_alias_glued_with_cyrillic_hyphen() -> None:
    """Аля-Алтайшина-111 → Алтайшина (границы — не буквы и не цифры)."""
    finder = BaseFinder(AliasContainer({'Алтайшина': ()}))
    correct, found = finder.find_word_in_title('8.25R20 алтайшина-111 10PR')
    assert correct == 'Алтайшина'
    assert found == 'алтайшина'


def test_find_alias_inside_word_is_not_found() -> None:
    """Алиас внутри другого слова (без границ) не находится."""
    finder = BaseFinder(AliasContainer({'Nortec': ()}))
    correct, found = finder.find_word_in_title('nortecx')
    assert correct is None
    assert found is None
