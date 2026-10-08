"""Тесты config-driven парсера (этап 3): хуки делегируют стратегиям."""

from unittest.mock import MagicMock

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.config_driven_parser import strategy_hooks_from_section
from parsers.base_parser.manufacturer_finder import ManufacturerFinder
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.vendor_config.models import VendorConfig

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
    mock.manufacturer_aliases.return_value = {}
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
    strategy.resolve.assert_called_once_with(row, parser)


def test_manufacturer_correction_survives_title_recompose() -> None:
    """Бренд правится после финальной сборки title (иначе регистр затирается).

    Регресс: шаг ``title`` повторно собирает название из полей и затирал правку
    регистра, сделанную ``ManufacturerFinder`` в enrich (``TopTrust`` → ``Toptrust``).
    """
    strategy = MagicMock()
    strategy.prepare.return_value = '10-16.5 Toptrust L-2 10 TL'
    hooks = StrategyHooks(title=strategy, pipeline=('title',))
    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)
    parser._manufacturer_finder = ManufacturerFinder({'TopTrust': ()})

    row = RowItem({'title': '10-16.5 Toptrust L-2 10 TL', 'manufacturer_name': 'TopTrust'})
    parser.process_parsed_row(row)

    assert row.identity.title == '10-16.5 TopTrust L-2 10 TL'
    assert row.identity.manufacturer == 'TopTrust'


def test_manufacturer_found_after_pipeline_when_enrich_disabled() -> None:
    """Поиск производителя после title идёт даже при find_manufacturer_on_enrich=False (Пионер)."""
    strategy = MagicMock()
    strategy.prepare.return_value = '195/75R16 Triangle TR652'
    hooks = StrategyHooks(title=strategy, find_manufacturer_on_enrich=False, pipeline=('title',))
    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)
    parser._manufacturer_finder = ManufacturerFinder({'Triangle': ()})

    row = RowItem({'title': '195/75R16 TR652'})
    parser.process_parsed_row(row)

    assert row.identity.manufacturer == 'Triangle'


def test_manufacturer_from_category_reader_is_wired() -> None:
    """Пионер: производитель из раздела попадает в brand и в title."""
    config = VendorConfig.from_dict(
        {
            'enabled': 1,
            'code': '3',
            'name': 'Пионер',
            'start_row': 12,
            'file_templates': ['price*.xls'],
            'behavior': {
                'pipeline': ['category', 'min_rest', 'markup', 'title'],
                'find_manufacturer_on_enrich': False,
                'rest': 'minus_reserve',
            },
            'sections': [
                {
                    'id': '3',
                    'name': 'Пионер',
                    'columns': {'1': 'title', '2': 'price_opt', '4': 'rest_count', '5': 'reserve_count'},
                    'category': {'strategy': 'header_rows', 'zero_rest_categories': ['прочие']},
                    'title': {'strategy': 'manufacturer_from_category'},
                    'pricing': {'policy': 'map_on_opt'},
                }
            ],
        },
        'pioner',
        'pioner.json',
    )
    hooks = strategy_hooks_from_section(config.sections[0], config.behavior)
    assert hooks.category is not None
    assert hooks.title is not None

    hooks.category.resolve(RowItem({'title': 'Автошины TRIANGLE'}))
    row = RowItem({'title': 'Nortec ER-218', 'price_opt': 1000})
    prepared = hooks.title.prepare(row)

    assert row.identity.brand == 'triangle'
    assert prepared == 'Nortec triangle ER-218'


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
        find_manufacturer_on_enrich=False,
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
        find_manufacturer_on_enrich=False,
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


def test_zero_rest_when_category_unknown() -> None:
    """zero_rest_without_category обнуляет остаток строки без категории."""
    cat_strategy = MagicMock()
    cat_strategy.resolve.return_value = ''
    hooks = StrategyHooks(
        category=cat_strategy,
        find_manufacturer_on_enrich=False,
        zero_rest_without_category=True,
        pipeline=('category',),
    )
    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)

    row = RowItem({'title': 'Тест', 'price_opt': 1000, 'rest_count': 5})
    parser.process_parsed_row(row)

    assert row.stock.rest_count == 0


def test_rest_kept_without_category_when_flag_disabled() -> None:
    """Без флага остаток строки без категории сохраняется."""
    cat_strategy = MagicMock()
    cat_strategy.resolve.return_value = ''
    hooks = StrategyHooks(
        category=cat_strategy,
        find_manufacturer_on_enrich=False,
        pipeline=('category',),
    )
    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)

    row = RowItem({'title': 'Тест', 'price_opt': 1000, 'rest_count': 5})
    parser.process_parsed_row(row)

    assert row.stock.rest_count == 5


def test_pipeline_skips_missing_step() -> None:
    """Неизвестный шаг pipeline игнорируется."""
    cat_strategy = MagicMock()
    cat_strategy.resolve.return_value = 'Шина'

    hooks = StrategyHooks(
        category=cat_strategy,
        find_manufacturer_on_enrich=False,
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
