"""tests for TitleFilter: стоп-слова, чёрный список и подготовка title."""

import pytest
from test_parsers.test_vendors._test_providers import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    MarkupRulesProviderForTests,
)

from domain.row_item.row_item import RowItem
from parsers import data_provider
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfigNotSetError,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.title_filter import TitleFilter, strip_words_in_title

_SUPPLIER = ParseParamsSupplier(folder_name='test', name='Тест', code='99')
_TITLE = 'Michelin 185/65 R15 88H'


def _base_params() -> BasePriceParseConfigurationParams:
    return BasePriceParseConfigurationParams(
        black_list_provider=BlackListProviderForTests(),
        markup_rules_provider=MarkupRulesProviderForTests(),
        manufacturer_aliases=ManufacturerAliasesProviderForTests(),
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


def test_without_config_any_read_raises() -> None:
    """TitleFilter без конфига: любое чтение данных — ParseConfigNotSetError."""
    title_filter = TitleFilter(None)

    with pytest.raises(ParseConfigNotSetError):
        title_filter.get_black_list()
    with pytest.raises(ParseConfigNotSetError):
        title_filter.get_stop_words()


def test_reset_caches_forces_re_read() -> None:
    """Сброс кэшей заставляет перечитать black list и stop words."""
    title_filter = _title_filter()
    black_list = title_filter.get_black_list()

    assert title_filter.get_black_list() is black_list
    title_filter.reset_caches()
    assert title_filter.get_black_list() is not black_list


def test_prepare_black_list_strips_entries() -> None:
    prepared = _title_filter().prepare_black_list(['  некондиция  ', ''])
    assert prepared == ['некондиция', '']


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


def _title_filter_with(entries: list[str], masks: list[str]) -> TitleFilter:
    base_params = _base_params()
    config_params = base_params._replace(black_list_provider=_BlackListProvider(entries, masks))
    return TitleFilter(ParseConfiguration(config_params))
