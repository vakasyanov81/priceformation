"""tests for TitleFilter: стоп-слова, чёрный список и подготовка title."""

from typing import Any

from test_parsers.test_vendors._test_providers import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    MarkupRulesProviderForTests,
)

from domain.config_context import get_config_provider
from domain.row_item.row_item import RowItem
from parsers import data_provider
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.title_filter import TitleBlockList, TitleFilter, strip_words_in_title

_SUPPLIER = ParseParamsSupplier(folder_name='test', name='Тест', code='99')
_TITLE = 'Michelin 185/65 R15 88H'


def _base_params() -> BasePriceParseConfigurationParams:
    return BasePriceParseConfigurationParams(
        black_list_provider=BlackListProviderForTests(),
        markup_rules_provider=MarkupRulesProviderForTests(),
        manufacturer_aliases=ManufacturerAliasesProviderForTests(),
        config_provider=get_config_provider(),
        parser_params=ParserParams(
            supplier=_SUPPLIER,
            start_row=1,
            sheet_info='',
            columns={},
            stop_words=(),
            file_templates=(),
            sheet_indexes=(),
            row_item_adaptor=RowItem,
        ),
    )


def _title_filter() -> TitleFilter:
    return TitleFilter(ParseConfiguration(_base_params()))


def test_strip_words_in_title_collapses_spaces() -> None:
    assert strip_words_in_title('  385/65   R22.5  ') == '385/65 R22.5'


def test_strip_words_in_title_keeps_blank_as_is() -> None:
    """Пустая и состоящая из пробелов строка не меняется: вернуть её, а не нормализованную пустую."""
    assert strip_words_in_title('') == ''
    assert strip_words_in_title('   ') == '   '


def test_strip_words_in_title_none_stays_none() -> None:
    """None-заголовок возвращается как есть, а не превращается в заглушку."""
    missing_title: Any = None
    assert strip_words_in_title(missing_title) is None


def test_block_list_strips_black_list_entries() -> None:
    block_list = TitleBlockList(_config_with(['  некондиция  ', ''], []))
    assert block_list.black_list == ['некондиция', '']


def test_block_list_reads_config_once() -> None:
    block_list = TitleBlockList(_config_with(['некондиция'], ['*2 сорт*']))
    assert block_list.black_list is block_list.black_list
    assert block_list.stop_words is block_list.stop_words


def test_block_list_blocks_entry_and_mask() -> None:
    block_list = TitleBlockList(_config_with(['некондиция'], ['*2 сорт*']))
    assert block_list.blocks('некондиция')
    assert block_list.blocks('Шина 185/65 R15 2 сорт')
    assert not block_list.blocks(_TITLE)


def test_is_valid_title_rejects_empty() -> None:
    assert not _title_filter().is_valid_title('')
    assert not _title_filter().is_valid_title(None)


def test_is_valid_title_rejects_black_list_entry() -> None:
    title_filter = _title_filter_with(['некондиция'], [])
    assert not title_filter.is_valid_title('некондиция')
    assert title_filter.is_valid_title(_TITLE)


def test_is_valid_title_rejects_stop_word_mask() -> None:
    title_filter = _title_filter_with([], ['*2 сорт*'])
    assert not title_filter.is_valid_title('Шина 185/65 R15 2 сорт')
    assert title_filter.is_valid_title(_TITLE)


def test_get_prepared_title_returns_identity_title() -> None:
    row_item = RowItem({'title': _TITLE})
    assert _title_filter().get_prepared_title(row_item) == _TITLE
    assert RowItem({}).identity.title is None


class _BlackListProvider(data_provider.BlackListProviderBase):
    """Провайдер чёрного списка с заданными данными."""

    def __init__(self, entries: list[str], masks: list[str]) -> None:
        self._entries = entries
        self._masks = masks

    def get_black_list_data(self) -> list[str]:
        return self._entries

    def get_stop_words_data(self) -> list[str]:
        return self._masks


def _config_with(entries: list[str], masks: list[str]) -> ParseConfiguration:
    base_params = _base_params()
    return ParseConfiguration(base_params._replace(black_list_provider=_BlackListProvider(entries, masks)))


def _title_filter_with(entries: list[str], masks: list[str]) -> TitleFilter:
    return TitleFilter(_config_with(entries, masks))
