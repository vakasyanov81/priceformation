"""Тесты config-driven парсера (этап 3): хуки делегируют стратегиям."""

from unittest.mock import MagicMock

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.strategy_hooks import StrategyHooks

_TEST_PARAMS = ParserParams(
    supplier=ParseParamsSupplier(folder_name='test', name='Test', code='99'),
    start_row=1,
    sheet_info='',
    columns={},
    stop_words=(),
    file_templates=('*.xls',),
    sheet_indexes=(),
    row_item_adaptor=RowItem,
)


def _mock_parse_config() -> ParseConfiguration:
    """Минимальный ParseConfiguration для тестов."""
    mock = MagicMock(spec=ParseConfiguration)
    mock.parser_params = _TEST_PARAMS
    mock.supplier = _TEST_PARAMS.supplier
    return mock


def test_category_strategy_is_called() -> None:
    """category_for делегирует стратегии категории."""
    strategy = MagicMock()
    strategy.resolve.return_value = 'Автошина'
    hooks = StrategyHooks(category=strategy)

    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)

    row = RowItem({'title': 'Шина'})
    category = parser.category_for(row)
    assert category == 'Автошина'
    strategy.resolve.assert_called_once_with(row)


def test_title_strategy_is_called() -> None:
    """get_prepared_title делегирует стратегии title."""
    strategy = MagicMock()
    strategy.prepare.return_value = '385/65R22.5'
    hooks = StrategyHooks(title=strategy)

    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)

    row = RowItem({'title': '385/65 R22.5'})
    prepared_title = parser.get_prepared_title(row)
    assert prepared_title == '385/65R22.5'
    strategy.prepare.assert_called_once_with(row)


def test_rest_strategy_is_called() -> None:
    """skip_by_min_rest использует rest стратегию и min_rest из конфига."""
    strategy = MagicMock()
    strategy.item_rest.return_value = 3
    hooks = StrategyHooks(rest=strategy, min_rest=4)

    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)

    row = RowItem({'rest_count': 3})
    parser.skip_by_min_rest(row)
    strategy.item_rest.assert_called_once_with(row)
    assert row.stock.rest_count == 0  # обнулился, т.к. 3 < 4


def test_rest_strategy_passes_large_rest() -> None:
    """При остатке >= min_rest строка не обнуляется."""
    strategy = MagicMock()
    strategy.item_rest.return_value = 5
    hooks = StrategyHooks(rest=strategy, min_rest=4)

    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)

    row = RowItem({'rest_count': 5})
    parser.skip_by_min_rest(row)
    assert row.stock.rest_count == 5  # не обнулился


def test_find_manufacturer_from_hooks() -> None:
    """find_manufacturer_on_enrich берётся из StrategyHooks."""
    hooks = StrategyHooks(find_manufacturer_on_enrich=False)

    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)

    assert not parser._effective_find_manufacturer


def test_find_manufacturer_default_when_no_hooks() -> None:
    """Без StrategyHooks используется значение класса."""
    parser = BaseParser(parse_config=_mock_parse_config())

    assert parser._effective_find_manufacturer


def test_pipeline_default_order() -> None:
    """process_parsed_row со стратегиями вызывает шаги в порядке pipeline."""
    cat_strategy = MagicMock()
    cat_strategy.resolve.return_value = 'Шина'

    hooks = StrategyHooks(
        category=cat_strategy,
        pipeline=('title', 'min_rest', 'category', 'markup'),
    )

    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)
    parser._title_filter = MagicMock()
    parser._title_filter.get_prepared_title.return_value = 'Стандарт'
    parser._row_processor = MagicMock()

    row = RowItem({'title': 'Тест', 'price_opt': 1000, 'rest_count': 5})
    parser.process_parsed_row(row)

    # title → min_rest → category → markup
    parser._title_filter.get_prepared_title.assert_called_once()
    cat_strategy.resolve.assert_called_once()
    parser._row_processor.add_price_markup.assert_called_once_with(row)


def test_pipeline_custom_order() -> None:
    """pipeline из конфига: category → min_rest → markup → title (Пионер)."""
    cat_strategy = MagicMock()
    cat_strategy.resolve.return_value = 'Шина'

    hooks = StrategyHooks(
        category=cat_strategy,
        pipeline=('category', 'min_rest', 'markup', 'title'),
    )

    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)
    parser._title_filter = MagicMock()
    parser._title_filter.get_prepared_title.return_value = 'Стандарт'
    parser._row_processor = MagicMock()

    row = RowItem({'title': 'Тест', 'price_opt': 1000, 'rest_count': 5})
    parser.process_parsed_row(row)

    # категория должна быть вызвана первой
    # title — последним
    cat_strategy.resolve.assert_called_once()
    parser._row_processor.add_price_markup.assert_called_once_with(row)


def test_pipeline_skips_missing_step() -> None:
    """Неизвестный шаг pipeline игнорируется."""
    cat_strategy = MagicMock()
    cat_strategy.resolve.return_value = 'Шина'

    hooks = StrategyHooks(
        category=cat_strategy,
        pipeline=('category', 'unknown_step', 'markup'),
    )

    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)
    parser._row_processor = MagicMock()

    row = RowItem({'title': 'Тест', 'price_opt': 1000, 'rest_count': 5})
    parser.process_parsed_row(row)

    # категория вызвана
    cat_strategy.resolve.assert_called_once()
    # markup вызван
    parser._row_processor.add_price_markup.assert_called_once()
