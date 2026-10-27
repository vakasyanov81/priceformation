"""RowEnricher: отсев и подготовка строк на заглушках сервисов — без BaseParser."""

import logging
from typing import NamedTuple
from unittest.mock import MagicMock

import pytest

from domain.row_item.row_item import RowItem
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.row_enricher import RowEnricher

_SUPPLIER = 'Поставщик'
_START_ROW = 3
_TITLE = '205/55R16 Test'
_BAD_TITLE = 'bad'


class _Setup(NamedTuple):
    enricher: RowEnricher
    titles: MagicMock
    categories: MagicMock
    manufacturers: MagicMock
    stats: ParserStats


def _setup() -> _Setup:
    settings = MagicMock()
    settings.title.return_value = _SUPPLIER
    settings.parser_params.return_value.start_row = _START_ROW
    settings.parser_params.return_value.supplier.name = _SUPPLIER
    titles = MagicMock()
    titles.is_valid_title.side_effect = lambda title: bool(title) and title != _BAD_TITLE
    categories = MagicMock()
    manufacturers = MagicMock()
    stats = ParserStats()
    enricher = RowEnricher(settings, titles, categories, manufacturers, stats)
    return _Setup(enricher, titles, categories, manufacturers, stats)


def test_enrich_runs_services_and_sets_service_fields() -> None:
    setup = _setup()
    row = RowItem({'title': _TITLE, 'season': 'зима', 'spike': 'ш.'})

    assert setup.enricher.enrich([row]) == [row]

    setup.titles.set_prepared_title.assert_called_once_with(row)
    setup.manufacturers.apply_manufacturer.assert_called_once_with(row)
    setup.categories.lookup.correction_category.assert_called_once_with(row)
    assert row.vendor.supplier_name == _SUPPLIER
    assert row.tire.spike == 'Да'
    assert row.tire.season == 'Зимняя'


def test_enrich_drops_invalid_title_and_counts_only_non_empty() -> None:
    setup = _setup()
    kept = RowItem({'title': _TITLE})

    dropped = [RowItem({'title': _BAD_TITLE}), RowItem({})]

    assert setup.enricher.enrich([*dropped, kept]) == [kept]
    assert setup.stats.black_list_skips == 1


def test_enrich_logs_title_error_with_row_number(caplog: pytest.LogCaptureFixture) -> None:
    setup = _setup()
    setup.titles.set_prepared_title.side_effect = ValueError('boom')

    with caplog.at_level(logging.ERROR):
        assert setup.enricher.enrich([RowItem({'title': _TITLE})]) == []

    assert f'(№ {_START_ROW})' in caplog.text
    assert _SUPPLIER in caplog.text


def test_enrich_drops_rows_with_parse_errors(caplog: pytest.LogCaptureFixture) -> None:
    setup = _setup()
    broken = RowItem({'title': _TITLE, 'rest_count': 'много'})

    with caplog.at_level(logging.ERROR):
        assert setup.enricher.enrich([broken]) == []

    assert f'(№ {_START_ROW})' in caplog.text


def test_keep_requires_price_when_rest_present() -> None:
    setup = _setup()
    priced = RowItem({'title': _TITLE, 'rest_count': 5, 'price_opt': 100})
    no_price = RowItem({'title': _TITLE, 'rest_count': 5})
    blacklisted = RowItem({'title': _BAD_TITLE, 'rest_count': 5, 'price_opt': 100})

    assert setup.enricher.keep([priced, no_price, blacklisted]) == [priced]
    assert setup.stats.black_list_skips == 1
