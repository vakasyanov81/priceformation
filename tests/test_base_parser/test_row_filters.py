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

from domain.config_context import get_config_provider
from domain.row_item.row_item import RowItem
from parsers.base_parser import parser_settings as base_parser_module
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    BasePriceParseConfigurationParams,
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.category_service import CategoryLookup, CategoryService
from parsers.base_parser.parser_settings import ParserSettings
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.row_filters import DEFAULT_MIN_REST, drop_empty_rest

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


def _parser() -> BaseParser:
    return BaseParser(parse_config=ParseConfiguration(_base_params()))


def _parser_with_finder() -> BaseParser:
    parser = _parser()
    parser.enricher.categories.lookup.reset()
    return parser


def _priced(title: str) -> RowItem:
    return RowItem({'title': title, 'rest_count': _REST, 'price_opt': _PRICE})


def test_correction_category_skips_without_finder() -> None:
    parser = _parser()
    row = RowItem({'type_production': 'грузовая'})
    parser.enricher.categories.lookup.correction_category(row)
    assert row.vendor.type_production == 'грузовая'


def test_correction_category_skips_empty_type() -> None:
    parser = _parser_with_finder()
    row = RowItem({})
    parser.enricher.categories.lookup.correction_category(row)
    assert not row.vendor.type_production


def test_correction_category_maps_alias() -> None:
    parser = _parser_with_finder()
    row = RowItem({'type_production': 'грузовая'})
    parser.enricher.categories.lookup.correction_category(row)
    assert row.vendor.type_production == 'Грузовая шина'


def test_drop_row_with_rest_and_no_purchase_price() -> None:
    parser = _parser()
    dropped = RowItem({'title': _TITLE, 'rest_count': _REST})
    kept = RowItem({'title': _TITLE, 'rest_count': _REST, 'price_opt': _PRICE})
    assert parser.enricher.keep([dropped, kept]) == [kept]


def test_drop_empty_rest_requires_opt_and_rest() -> None:
    kept = RowItem({'title': _TITLE, 'rest_count': _REST, 'price_opt': _PRICE})
    no_rest = RowItem({'title': _TITLE, 'price_opt': _PRICE})
    no_opt = RowItem({'title': _TITLE, 'rest_count': _REST})
    zero_rest = RowItem({'title': _TITLE, 'rest_count': 0, 'price_opt': _PRICE})
    assert drop_empty_rest([kept, no_rest, no_opt, zero_rest]) == [kept]


def test_is_valid_title_keeps_normal() -> None:
    assert _parser().enricher.titles.is_valid_title(_TITLE)


def test_is_valid_title_rejects_empty() -> None:
    assert not _parser().enricher.titles.is_valid_title('')


def test_is_valid_title_rejects_exact_blacklist() -> None:
    assert not _parser().enricher.titles.is_valid_title('wrong title')


def test_is_valid_title_rejects_mask() -> None:
    assert not _parser().enricher.titles.is_valid_title('some некондиция product')


def test_filter_keep_counts_exact_blacklist() -> None:
    parser = _parser()
    kept = _priced(_TITLE)
    assert parser.enricher.keep([_priced('wrong title'), kept]) == [kept]
    assert parser.stats.black_list_skips == 1


def test_filter_keep_counts_mask() -> None:
    parser = _parser()
    parser.enricher.keep([_priced('some некондиция product')])
    assert parser.stats.black_list_skips == 1


def test_filter_keep_does_not_count_missing_price() -> None:
    parser = _parser()
    parser.enricher.keep([RowItem({'title': _TITLE, 'rest_count': _REST})])
    assert parser.stats.black_list_skips == 0


def test_enrich_counts_blacklist_after_title() -> None:
    parser = _parser()
    kept = _priced(_TITLE)
    kept_rows = parser.enricher.enrich([_priced('wrong title 2'), kept])
    assert [row_item.identity.title for row_item in kept_rows] == [_TITLE]
    assert parser.stats.black_list_skips == 1


def test_after_process_counts_titles_not_composed() -> None:
    """Итог разбора считает позиции, у которых название шины не собралось из полей."""
    parser = _parser()
    parser.parsed_items = [
        RowItem({'title': _TITLE, 'rest_count': _REST, 'price_opt': _PRICE, 'title_not_composed': True}),
        RowItem({'title': _TITLE, 'rest_count': _REST, 'price_opt': _PRICE}),
    ]

    parser.after_process()

    assert parser.stats.titles_not_composed == 1


def test_enrich_empty_title_not_counted() -> None:
    parser = _parser()
    assert parser.enricher.enrich([RowItem({})]) == []
    assert parser.stats.black_list_skips == 0


def test_enrich_skips_title_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """ValueError от set_prepared_title логируется, строка пропускается."""
    parser = _parser()

    # Мокаем set_prepared_title, чтобы он выбросил ValueError с любым title
    def _raise_on_title(row_item: RowItem) -> bool:
        if row_item.identity.title:
            raise ValueError('bad title')
        return True

    monkeypatch.setattr(parser.enricher.titles, 'set_prepared_title', _raise_on_title)
    rows = parser.enricher.enrich([_priced(_TITLE)])
    assert rows == []


def test_enrich_row_item_sets_service_fields() -> None:
    """enrich проставляет поставщика, шип и канонический сезон по ключам."""
    parser = _parser()
    row = RowItem({'title': _TITLE, 'season': 'лето', 'spike': 'да'})

    parser.enricher.enrich([row])

    assert row.get_field('supplier_name') == 'Тест'
    assert row.get_field('spike') == 'Да'
    assert row.get_field('season') == 'Летняя'


def _params_with_sheet_info(sheet_info: str) -> BasePriceParseConfigurationParams:
    base = _base_params()
    return BasePriceParseConfigurationParams(
        black_list_provider=base.black_list_provider,
        markup_rules_provider=base.markup_rules_provider,
        manufacturer_aliases=base.manufacturer_aliases,
        config_provider=get_config_provider(),
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
    """До разбора files — None, а не пустая строка."""
    parser = _parser()
    assert parser.price_files.files is None


def test_repr_includes_sheet_info() -> None:
    """repr показывает поставщика и лист, если лист задан в конфиге."""
    parser = BaseParser(parse_config=ParseConfiguration(_params_with_sheet_info(_SHEET_INFO)))
    assert repr(parser) == f'Тест ({_SHEET_INFO})'


def test_default_min_rest_is_four() -> None:
    assert DEFAULT_MIN_REST == 4


def test_category_for_without_hooks_is_none() -> None:
    """Без стратегий категория не ищется (не падает на None.category)."""
    assert _parser().enricher.categories.category_for(RowItem({'title': _TITLE})) is None


class _DiskCategories(CategoryService):
    """Категория, зависящая от строки."""

    def category_for(self, row_item: RowItem) -> str | None:
        return None if row_item is None else 'Диск'


def test_apply_category_sets_type_production() -> None:
    """Категория строки попадает в type_production по правильному ключу."""
    parser = _parser()
    parser.enricher.categories = _DiskCategories(None, CategoryLookup(parser.stats))
    row = RowItem({'title': _TITLE})
    parser.enricher.categories.apply_category(row)
    assert row.vendor.type_production == 'Диск'


def test_apply_manufacturer_calls_finder() -> None:
    """apply_manufacturer запускает поиск, пока включён флаг."""
    parser = _parser()
    finder = MagicMock()
    parser.settings._manufacturer_finder = finder
    parser.enricher.manufacturers.apply_manufacturer(RowItem({'title': _TITLE}))
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
    assert parser.settings.manufacturer_finder() is sentinel
    assert captured['aliases'] == parser.settings.parse_config().manufacturer_aliases()


def test_raw_parse_passes_file_path_to_reader() -> None:
    """raw_parse прокидывает путь файла в читатель."""
    parser = _parser()
    reader = MagicMock()
    parser.price_files.file_reader = reader
    parser.price_files.raw_parse('price.xls')
    reader.raw_parse.assert_called_once_with('price.xls', parser.settings.parser_params())


class _NoPriceFiles(PriceFiles):
    """Коллаборатор без файлов: parse() не лезет в папку поставщика."""

    def __init__(self) -> None:
        super().__init__(ParserSettings(), MagicMock())

    def resolve(self) -> list[str]:
        self.files = []
        return self.files


class _ResetSpyLookup(CategoryLookup):
    reset_calls = 0

    def reset(self) -> None:
        self.reset_calls += 1
        super().reset()


def test_parse_creates_category_finder() -> None:
    """parse() готовит CategoryFinder до обработки строк."""
    parser = _parser()
    parser.price_files = _NoPriceFiles()
    parser.enricher.categories.lookup = _ResetSpyLookup(parser.stats)
    parser.parse()
    assert parser.enricher.categories.lookup.reset_calls == 1


def _parser_with_start_row(start_row: int) -> BaseParser:
    """Парсер, у которого первая строка прайса имеет заданный номер."""
    base = _base_params()
    config_params = base._replace(parser_params=dataclasses.replace(base.parser_params, start_row=start_row))
    return BaseParser(parse_config=ParseConfiguration(config_params))


def test_keep_row_item_counts_each_skip() -> None:
    """Счётчик пропусков накапливается, а не обнуляется в единицу."""
    parser = _parser()

    assert parser.enricher.keep([_priced('wrong title')]) == []
    assert parser.enricher.keep([_priced('wrong title 2')]) == []
    assert parser.stats.black_list_skips == 2


def test_enrich_counts_each_blacklist_skip() -> None:
    """enrich накапливает пропуски по чёрному списку, а не пишет 1."""
    parser = _parser()

    parser.enricher.enrich([_priced('wrong title'), _priced('wrong title 2')])

    assert parser.stats.black_list_skips == 2


def test_enrich_logs_row_number_from_start_row(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Номер строки в логе пропуска берётся из start_row, а не с нуля и не None."""
    parser = _parser_with_start_row(5)

    def _raise_on_title(row_item: RowItem) -> bool:
        raise ValueError('bad title')

    monkeypatch.setattr(parser.enricher.titles, 'set_prepared_title', _raise_on_title)

    with caplog.at_level(logging.ERROR):
        parser.enricher.enrich([_priced(_TITLE)])

    assert '(№ 5)' in caplog.text
