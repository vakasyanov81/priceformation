"""tests for category correction, title strip and purchase-price filter."""

import dataclasses
import logging
from unittest.mock import MagicMock

import pytest
from test_parsers.test_vendors._test_providers import (
    BlackListProviderForTests,
    ManufacturerAliasesProviderForTests,
    MarkupRulesProviderForTests,
)

from domain.row_item.row_item import RowItem
from parsers.base_parser import base_parser as base_parser_module
from parsers.base_parser.base_parser import BaseParser, _type_production_from_filename
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.base_parser_row import _enrich_row_item, _keep_row_item, drop_empty_rest, enrich_items
from parsers.base_parser.category_finder import CategoryFinder

_SUPPLIER = ParseParamsSupplier(folder_name='test', name='Тест', code='99')
_TITLE = 'ok title'
_REST = 5
_PRICE = 100
_SHEET_INFO = 'Лист1'


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


def _parser() -> BaseParser:
    return BaseParser(parse_config=ParseConfiguration(_base_params()))


def _parser_with_finder() -> BaseParser:
    parser = _parser()
    parser._category_finder = CategoryFinder()  # noqa: WPS437
    return parser


def _priced(title: str) -> RowItem:
    return RowItem({'title': title, 'rest_count': _REST, 'price_opt': _PRICE})


def test_correction_category_skips_without_finder() -> None:
    parser = _parser()
    row = RowItem({'type_production': 'грузовая'})
    parser.correction_category(row)
    assert row.vendor.type_production == 'грузовая'


def test_correction_category_skips_empty_type() -> None:
    parser = _parser_with_finder()
    row = RowItem({})
    parser.correction_category(row)
    assert not row.vendor.type_production


def test_correction_category_maps_alias() -> None:
    parser = _parser_with_finder()
    row = RowItem({'type_production': 'грузовая'})
    parser.correction_category(row)
    assert row.vendor.type_production == 'Грузовая шина'


def test_strip_words_collapses_spaces() -> None:
    assert BaseParser.strip_words_in_title('  385/65   R22.5  ') == '385/65 R22.5'


def test_strip_words_keeps_empty_and_whitespace() -> None:
    assert BaseParser.strip_words_in_title('') == ''
    assert BaseParser.strip_words_in_title('   ') == '   '


def test_drop_row_with_rest_and_no_purchase_price() -> None:
    parser = _parser()
    dropped = RowItem({'title': _TITLE, 'rest_count': _REST})
    kept = RowItem({'title': _TITLE, 'rest_count': _REST, 'price_opt': _PRICE})
    assert parser.filter_keep([dropped, kept]) == [kept]


def test_drop_empty_rest_requires_opt_and_rest() -> None:
    kept = RowItem({'title': _TITLE, 'rest_count': _REST, 'price_opt': _PRICE})
    no_rest = RowItem({'title': _TITLE, 'price_opt': _PRICE})
    no_opt = RowItem({'title': _TITLE, 'rest_count': _REST})
    zero_rest = RowItem({'title': _TITLE, 'rest_count': 0, 'price_opt': _PRICE})
    assert drop_empty_rest([kept, no_rest, no_opt, zero_rest]) == [kept]


def test_is_valid_title_keeps_normal() -> None:
    assert _parser().is_valid_title(_TITLE)


def test_is_valid_title_rejects_empty() -> None:
    assert not _parser().is_valid_title('')


def test_is_valid_title_rejects_exact_blacklist() -> None:
    assert not _parser().is_valid_title('wrong title')


def test_is_valid_title_rejects_mask() -> None:
    assert not _parser().is_valid_title('some некондиция product')


def test_filter_keep_counts_exact_blacklist() -> None:
    parser = _parser()
    kept = _priced(_TITLE)
    assert parser.filter_keep([_priced('wrong title'), kept]) == [kept]
    assert parser.stats.black_list_skips == 1


def test_filter_keep_counts_mask() -> None:
    parser = _parser()
    parser.filter_keep([_priced('some некондиция product')])
    assert parser.stats.black_list_skips == 1


def test_filter_keep_does_not_count_missing_price() -> None:
    parser = _parser()
    parser.filter_keep([RowItem({'title': _TITLE, 'rest_count': _REST})])
    assert parser.stats.black_list_skips == 0


def test_enrich_counts_blacklist_after_title() -> None:
    parser = _parser()
    kept = _priced(_TITLE)
    kept_rows = enrich_items(parser, [_priced('wrong title 2'), kept])
    assert [row_item.identity.title for row_item in kept_rows] == [_TITLE]
    assert parser.stats.black_list_skips == 1


def test_enrich_empty_title_not_counted() -> None:
    parser = _parser()
    assert enrich_items(parser, [RowItem({})]) == []
    assert parser.stats.black_list_skips == 0


def test_enrich_skips_title_value_error() -> None:
    """ValueError от set_prepared_title логируется, строка пропускается."""
    parser = _parser()

    # Мокаем set_prepared_title, чтобы он выбросил ValueError с любым title
    def _raise_on_title(row_item: RowItem) -> bool:
        if row_item.identity.title:
            raise ValueError('bad title')
        return True

    parser.set_prepared_title = _raise_on_title  # type: ignore[method-assign]
    rows = enrich_items(parser, [_priced(_TITLE)])
    assert rows == []


def test_enrich_row_item_sets_service_fields() -> None:
    """_enrich_row_item проставляет поставщика, шип и канонический сезон по ключам."""
    parser = MagicMock()
    parser.parser_params.return_value.supplier.name = 'Тест'
    parser.get_spike_title.return_value = 'Да'
    row = RowItem({'title': _TITLE, 'season': 'лето'})

    _enrich_row_item(parser, row)

    assert row.get_field('supplier_name') == 'Тест'
    assert row.get_field('spike') == 'Да'
    assert row.get_field('season') == 'Летняя'


def _params_with_sheet_info(sheet_info: str) -> BasePriceParseConfigurationParams:
    base = _base_params()
    return BasePriceParseConfigurationParams(
        black_list_provider=base.black_list_provider,
        markup_rules_provider=base.markup_rules_provider,
        manufacturer_aliases=base.manufacturer_aliases,
        parser_params=ParserParams(
            supplier=base.parser_params.supplier,
            start_row=base.parser_params.start_row,
            sheet_info=sheet_info,
            columns=base.parser_params.columns,
            stop_words=base.parser_params.stop_words,
            file_templates=base.parser_params.file_templates,
            sheet_indexes=base.parser_params.sheet_indexes,
            row_item_adaptor=base.parser_params.row_item_adaptor,
        ),
    )


def test_parser_initial_optional_state_is_none() -> None:
    """До разбора type_production и files — None, а не пустая строка."""
    parser = _parser()
    assert parser.type_production is None
    assert parser.files is None


def test_repr_includes_sheet_info() -> None:
    """repr показывает поставщика и лист, если лист задан в конфиге."""
    parser = BaseParser(parse_config=ParseConfiguration(_params_with_sheet_info(_SHEET_INFO)))
    assert repr(parser) == f'Тест ({_SHEET_INFO})'


def test_get_min_rest_count_is_four() -> None:
    assert BaseParser.get_min_rest_count() == 4


def test_strip_words_in_title_none_stays_none() -> None:
    """None-заголовок не превращается в подставную строку."""
    assert BaseParser.strip_words_in_title(None) is None  # type: ignore[arg-type]


def test_type_production_from_filename_without_underscore() -> None:
    """Имя без `_` целиком; иначе берётся хвост после последнего `_`."""
    assert _type_production_from_filename('disks.xls') == 'disks.xls'
    assert _type_production_from_filename('brand_cat_disks.xls') == 'disks.xls'


def test_category_for_without_hooks_is_none() -> None:
    """Без стратегий категория не ищется (не падает на None.category)."""
    assert _parser().category_for(RowItem({'title': _TITLE})) is None


class _CategoryParser(BaseParser):
    """Парсер с категорией, зависящей от строки."""

    def category_for(self, row_item: RowItem) -> str | None:
        return None if row_item is None else 'Диск'


def test_apply_category_sets_type_production() -> None:
    """Категория строки попадает в type_production по правильному ключу."""
    parser = _CategoryParser(parse_config=ParseConfiguration(_base_params()))
    row = RowItem({'title': _TITLE})
    parser.apply_category(row)
    assert row.vendor.type_production == 'Диск'


def test_apply_manufacturer_calls_finder() -> None:
    """apply_manufacturer запускает поиск, пока включён флаг."""
    parser = _parser()
    finder = MagicMock()
    parser._manufacturer_finder = finder  # noqa: WPS437
    parser.apply_manufacturer(RowItem({'title': _TITLE}))
    finder.process.assert_called_once()


def test_manufacturer_finder_uses_config_aliases(monkeypatch: pytest.MonkeyPatch) -> None:
    """Манипулятор строится на алиасах из конфига, а не на None."""
    parser = _parser()
    captured: dict[str, object] = {}
    sentinel = object()

    def _fake(aliases: object) -> object:
        captured['aliases'] = aliases
        return sentinel

    monkeypatch.setattr(base_parser_module, 'ManufacturerFinder', _fake)
    assert parser.manufacturer_finder() is sentinel
    assert captured['aliases'] == parser.parse_config().manufacturer_aliases()


def test_set_parse_config_resets_manufacturer_finder() -> None:
    """Смена конфига сбрасывает закэшированный манипулятор в None."""
    parser = _parser()
    parser._manufacturer_finder = MagicMock()  # noqa: WPS437
    parser.set_parse_config(ParseConfiguration(_base_params()))
    assert parser._manufacturer_finder is None  # noqa: WPS437


def test_raw_parse_passes_file_path_to_reader() -> None:
    """raw_parse прокидывает путь файла в читатель."""
    parser = _parser()
    parser._file_reader_impl = MagicMock()  # noqa: WPS437
    parser.raw_parse('price.xls')
    parser._file_reader_impl.raw_parse.assert_called_once_with('price.xls', parser.parser_params())  # noqa: WPS437


def test_parse_creates_category_finder() -> None:
    """parse() готовит CategoryFinder до обработки строк."""
    parser = _parser()
    parser._price_files = list  # type: ignore[method-assign]
    parser.parse()
    assert parser._category_finder is not None  # noqa: WPS437


def _parser_with_start_row(start_row: int) -> BaseParser:
    """Парсер, у которого первая строка прайса имеет заданный номер."""
    base = _base_params()
    config_params = base._replace(parser_params=dataclasses.replace(base.parser_params, start_row=start_row))
    return BaseParser(parse_config=ParseConfiguration(config_params))


def test_keep_row_item_counts_each_skip() -> None:
    """Счётчик пропусков накапливается, а не обнуляется в единицу."""
    parser = _parser()

    assert _keep_row_item(parser, _priced('wrong title')) is False
    assert _keep_row_item(parser, _priced('wrong title 2')) is False
    assert parser.stats.black_list_skips == 2


def test_enrich_counts_each_blacklist_skip() -> None:
    """enrich накапливает пропуски по чёрному списку, а не пишет 1."""
    parser = _parser()

    enrich_items(parser, [_priced('wrong title'), _priced('wrong title 2')])

    assert parser.stats.black_list_skips == 2


def test_enrich_logs_row_number_from_start_row(caplog: pytest.LogCaptureFixture) -> None:
    """Номер строки в логе пропуска берётся из start_row, а не с нуля и не None."""
    parser = _parser_with_start_row(5)

    def _raise_on_title(row_item: RowItem) -> bool:
        raise ValueError('bad title')

    parser.set_prepared_title = _raise_on_title  # type: ignore[method-assign]

    with caplog.at_level(logging.ERROR):
        enrich_items(parser, [_priced(_TITLE)])

    assert '(№ 5)' in caplog.text
