"""tests for BaseFinder alias search."""

from pathlib import Path

import pytest

from domain.protocols import ConfigProvider
from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.alias_search import _has_word_boundaries, find_bounded
from parsers.base_parser.base_finder import BaseFinder
from parsers.data_provider.manufacturer_aliases import ManufacturerAliasesProviderFromUserConfig, aliases_for_finder


def test_title_lower_none_before_find() -> None:
    """title_lower = None при невызванном find_word_in_title."""
    finder = BaseFinder(AliasContainer({'A': ()}))
    assert finder.title_lower is None


def test_find_empty_alias_returns_minus_one() -> None:
    """Пустой алиас не ищется: guard возвращает -1, а не позицию нуля."""
    assert find_bounded(' abc', '') == -1


def test_find_returns_first_bounded_occurrence() -> None:
    """Следующее совпадение ищется вперёд от позиции, а не с конца строки."""
    assert find_bounded('xbrand brand brand', 'brand') == 7


def test_find_symbol_alias_after_rejected_occurrence() -> None:
    """Небуквенный алиас может иметь допустимое совпадение сразу после отвергнутого."""
    assert find_bounded('a++ ', '+') == 2


def test_has_word_boundaries_rejects_alnum_before() -> None:
    """Буква/цифра перед алиасом — не граница слова."""
    assert _has_word_boundaries('ab', 1, 1) is False


def test_find_word_in_title_caches_by_title() -> None:
    """Повторный title не перебирает алиасы заново, результат тот же."""
    finder = BaseFinder(AliasContainer({'Brand': ('brnd',)}))
    first = finder.find_word_in_title('xx brnd yy')
    finder._found['xx brnd yy'] = ('cached', None)
    assert first == ('Brand', 'brnd')
    assert finder.find_word_in_title('xx brnd yy') == ('cached', None)


def test_empty_canonical_name_allows_bracket_fallback(fake_config_provider: ConfigProvider) -> None:
    """Пустое каноническое имя из JSON не останавливает поиск бренда в скобках."""
    config_path = Path(fake_config_provider.config_file('manufacturer_aliases.json'))
    config_path.write_text('{"": ["Unknown"], "Brand": []}', encoding='utf-8')
    aliases = ManufacturerAliasesProviderFromUserConfig(fake_config_provider).get_aliases()
    finder = BaseFinder(AliasContainer(aliases_for_finder(aliases)))

    assert finder.find_word_in_title('Unknown (Brand)') == ('Brand', 'Brand')


@pytest.mark.parametrize(
    ('alias', 'title', 'expected_canonical', 'expected_found'),
    [
        pytest.param('Brand', 'xx Brand yy BRAND zz', 'Brand', 'Brand', id='uses_first_alias_occurrence'),
        pytest.param('НКШЗ', 'НКШЗ', 'НКШЗ', 'НКШЗ', id='title_equal_to_alias'),
        pytest.param('НКШЗ', 'НКШЗ 175R16', 'НКШЗ', 'НКШЗ', id='alias_at_start_of_title'),
        pytest.param('Bridgestone', 'шина Bridgestone', 'Bridgestone', 'Bridgestone', id='alias_at_end_of_title'),
        pytest.param('A', '', None, None, id='with_empty_title_returns_none'),
        pytest.param('B', 'ABC', None, None, id='alias_no_whitespace_wrap'),
        pytest.param('Nortec', 'Диск штамп nortec-16 11.75x22.5', 'Nortec', 'nortec', id='alias_glued_with_hyphen'),
        pytest.param(
            'Алтайшина', '8.25R20 алтайшина-111 10PR', 'Алтайшина', 'алтайшина', id='alias_glued_with_cyrillic_hyphen'
        ),
        pytest.param('Nortec', 'nortecx', None, None, id='alias_inside_word_is_not_found'),
        pytest.param('Brand', ' Brand', 'Brand', 'Brand', id='alias_at_position_one'),
    ],
)
def test_find_alias_boundaries(
    alias: str, title: str, expected_canonical: str | None, expected_found: str | None
) -> None:
    """Поиск сохраняет границы, регистр и первое допустимое совпадение алиаса."""
    finder = BaseFinder(AliasContainer({alias: ()}))
    assert finder.find_word_in_title(title) == (expected_canonical, expected_found)
