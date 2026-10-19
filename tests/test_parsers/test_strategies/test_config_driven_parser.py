"""Тесты config-driven парсера (этап 3): хуки делегируют стратегиям."""

import logging
from unittest.mock import MagicMock

import pytest
from log_watch import LoggerWatcher

from domain.exceptions import ConfigValidationError
from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.config_driven_parser import (
    _reader_for_config,
    make_config_driven_parser,
    parser_params_from_section,
    strategy_hooks_from_section,
    vendor_markup_policy_from_config,
)
from parsers.base_parser.manufacturer_finder import ManufacturerFinder
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.json_reader import JsonPriceReader
from parsers.strategies.category_fields import CategoryFields
from parsers.strategies.product_type import ProductTypeClassifier
from parsers.strategies.product_types import LIGHT_TRUCK, PASSENGER, TRUCK
from parsers.vendor_config.models import VendorConfig, VendorSection
from parsers.vendor_config.slot_configs import (
    BehaviorConfig,
    CategoryConfig,
    PricingConfig,
    TitleConfig,
)
from parsers.xls_reader import XlsReader

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


def _section(
    *,
    category: CategoryConfig | None = None,
    title: TitleConfig | None = None,
    pricing: PricingConfig | None = None,
) -> VendorSection:
    """Минимальная секция поставщика для проверки сборки парсера."""
    return VendorSection(
        id='sec1',
        name='Секция',
        start_row=5,
        file_templates=('price*.xls',),
        columns={0: 'title'},
        sheet_info='Лист1',
        sheet_indexes=(0,),
        category=category or CategoryConfig(),
        title=title or TitleConfig(),
        pricing=pricing or PricingConfig(),
    )


def test_parser_params_from_section_full() -> None:
    """Все поля секции переходят в ParserParams без потерь."""
    parser_params = parser_params_from_section(_section(), 'folder')

    assert parser_params == ParserParams(
        supplier=ParseParamsSupplier(folder_name='folder', name='Секция', code='sec1'),
        start_row=5,
        sheet_info='Лист1',
        columns={0: 'title'},
        stop_words=(),
        file_templates=('price*.xls',),
        sheet_indexes=(0,),
        row_item_adaptor=RowItem,
    )


@pytest.mark.parametrize(
    ('reader', 'expected'),
    [
        ('json', JsonPriceReader),
        ('xls', XlsReader),
        ('other', XlsReader),
    ],
)
def test_reader_for_config(reader: str, expected: type) -> None:
    """Тип ридера выбирается по значению reader конфига."""
    assert _reader_for_config(reader) is expected


def test_make_config_driven_parser_injects_hooks_and_reader() -> None:
    """Парсер получает хуки из секции и ридер из reader конфига."""
    section = _section(pricing=PricingConfig(policy='identity'))
    vendor_config = VendorConfig(
        folder='f',
        enabled=True,
        code='c',
        name='n',
        start_row=1,
        reader='json',
        sections=(section,),
    )

    parser = make_config_driven_parser(section, vendor_config, _mock_parse_config())

    assert parser._strategy_hooks is not None
    assert parser._strategy_hooks.min_rest == vendor_config.behavior.min_rest
    assert parser.data_reader is JsonPriceReader


def test_strategy_hooks_without_cities_have_no_warehouse_filter() -> None:
    assert strategy_hooks_from_section(_section(), BehaviorConfig(), 'mim').warehouse_filter is None


def test_strategy_hooks_with_cities_get_warehouse_filter() -> None:
    hooks = strategy_hooks_from_section(_section(), BehaviorConfig(warehouse_cities=('Новосибирск',)), 'mim')

    assert hooks.warehouse_filter is not None


def test_strategy_hooks_from_section_keeps_all_fields() -> None:
    """Все поведенческие поля behavior попадают в StrategyHooks."""
    behavior = BehaviorConfig(
        min_rest=7,
        zero_rest_without_category=True,
        find_manufacturer_on_enrich=False,
        pipeline=('category', 'markup'),
    )

    hooks = strategy_hooks_from_section(_section(), behavior)

    assert hooks.category is not None
    assert hooks.title is not None
    assert hooks.rest is not None
    assert hooks.min_rest == 7
    assert hooks.find_manufacturer_on_enrich is False
    assert hooks.zero_rest_without_category is True
    assert hooks.pipeline == ('category', 'markup')


@pytest.mark.parametrize(
    ('section', 'behavior', 'fragment'),
    [
        (_section(category=CategoryConfig(strategy='nope')), BehaviorConfig(), 'section sec1 category'),
        (_section(title=TitleConfig(strategy='nope')), BehaviorConfig(), 'section sec1 title'),
        (_section(), BehaviorConfig(rest='nope'), 'section sec1 rest'),
    ],
)
def test_strategy_hooks_error_carries_section_path(
    section: VendorSection,
    behavior: BehaviorConfig,
    fragment: str,
) -> None:
    """Ошибка стратегии несёт путь с id секции — по нему правят конфиг."""
    with pytest.raises(ConfigValidationError) as exc_info:
        strategy_hooks_from_section(section, behavior)

    assert str(exc_info.value).startswith(f'{fragment}:')


def test_vendor_markup_policy_error_carries_location() -> None:
    """Неизвестная политика наценки сообщает путь section.pricing."""
    with pytest.raises(ConfigValidationError) as exc_info:
        vendor_markup_policy_from_config(_section(pricing=PricingConfig(policy='nope')))

    assert str(exc_info.value).startswith('section.pricing:')


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


def test_strategy_hooks_build_category_fields_from_size_fields() -> None:
    """size_fields слота category превращаются в стратегию полей."""
    section = _section(category=CategoryConfig(size_fields={'Грузовая шина': {'season': 'Всесезонная'}}))

    hooks = strategy_hooks_from_section(section, BehaviorConfig())

    assert hooks.category_fields is not None
    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 18PR унив.ось'})
    hooks.category_fields.apply(row)
    assert row.tire.season == 'Всесезонная'


def test_strategy_hooks_without_size_fields_has_no_category_fields() -> None:
    """Без size_fields стратегия полей не создаётся."""
    hooks = strategy_hooks_from_section(_section(), BehaviorConfig())

    assert hooks.category_fields is None


def test_pipeline_applies_category_fields() -> None:
    """Шаг category применяет size_fields независимо от категории поставщика."""
    cat_strategy = MagicMock()
    cat_strategy.resolve.return_value = 'Автошина'
    hooks = StrategyHooks(
        category=cat_strategy,
        category_fields=CategoryFields({'Грузовая шина': {'season': 'Всесезонная'}}),
        pipeline=('category',),
    )
    parser = BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)

    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 18PR унив.ось'})
    parser.process_parsed_row(row)

    assert row.vendor.type_production == 'Автошина'
    assert row.tire.season == 'Всесезонная'


def test_strategy_hooks_builds_product_type_when_independent() -> None:
    """`calculate_type` в конфиге включает независимый классификатор."""
    section = _section(category=CategoryConfig(strategy='header_rows', calculate_type=True))

    hooks = strategy_hooks_from_section(section, BehaviorConfig())

    assert isinstance(hooks.product_type, ProductTypeClassifier)


def test_strategy_hooks_without_calculate_type_has_no_product_type() -> None:
    """По умолчанию слой независимого типа выключен."""
    hooks = strategy_hooks_from_section(_section(), BehaviorConfig())

    assert hooks.product_type is None


def _classifier_parser(declared: str) -> BaseParser:
    """Парсер с включённым независимым типом и заданным заявленным типом."""
    cat_strategy = MagicMock()
    cat_strategy.resolve.return_value = declared
    hooks = StrategyHooks(
        category=cat_strategy,
        product_type=ProductTypeClassifier(),
        pipeline=('category',),
    )
    return BaseParser(parse_config=_mock_parse_config(), strategy_hooks=hooks)


def test_apply_category_marks_concrete_mismatch() -> None:
    """Конкретное расхождение заявленного и своего типа помечается `type_corrected`."""
    parser = _classifier_parser(LIGHT_TRUCK)
    row = RowItem({'title': '275/65R20 112T'})

    parser.process_parsed_row(row)

    assert row.vendor.type_production == PASSENGER
    assert row.vendor.type_corrected is True


def test_apply_category_matching_declared_not_marked() -> None:
    """Совпадение своего типа с заявленным расхождением не считается."""
    parser = _classifier_parser(TRUCK)
    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 18PR унив.ось'})

    parser.process_parsed_row(row)

    assert row.vendor.type_production == TRUCK
    assert row.vendor.type_corrected is False


def test_apply_category_generic_declared_not_marked() -> None:
    """Общий заявленный ярлык не считается расхождением (README §7 п.4)."""
    parser = _classifier_parser('Автошина')
    row = RowItem({'title': '275/65R20 112T'})

    parser.process_parsed_row(row)

    assert row.vendor.type_production == PASSENGER
    assert row.vendor.type_corrected is False


def test_apply_category_logs_correction(watch_logger: LoggerWatcher) -> None:
    """Расхождение попадает в debug-лог с заявленным/вычисленным типом."""
    parser = _classifier_parser(LIGHT_TRUCK)
    watch = watch_logger('parsers.base_parser.base_parser', logging.DEBUG)

    parser.process_parsed_row(RowItem({'title': '275/65R20 112T'}))

    corrections = [message for _level, message in watch() if 'Тип товара изменён' in message]
    assert corrections == [
        f'Тип товара изменён: заявлено «{LIGHT_TRUCK}», вычислено «{PASSENGER}» // 275/65R20 112T',
    ]


def test_type_corrections_counts_only_rows_kept_in_price() -> None:
    """Счётчик расхождений не считает позиции, отброшенные без цены/остатка."""
    parser = _classifier_parser(LIGHT_TRUCK)
    kept = RowItem({'title': '275/65R20 112T', 'price_opt': 100, 'rest_count': 4})
    dropped = RowItem({'title': '275/65R20 112T', 'price_opt': 0, 'rest_count': 0})
    for row_item in (kept, dropped):
        parser.process_parsed_row(row_item)
    parser.parsed_items = [kept, dropped]

    parser.after_process()

    assert kept.vendor.type_corrected is True
    assert dropped.vendor.type_corrected is True
    assert parser.stats.type_corrections == 1


def test_apply_category_matching_does_not_count() -> None:
    """Совпавший тип расхождением не помечается и счётчик не увеличивает."""
    parser = _classifier_parser(TRUCK)
    row = RowItem({'title': '10.00 R20 DOUBLEROAD DR-801 18PR унив.ось', 'price_opt': 100, 'rest_count': 4})
    parser.process_parsed_row(row)
    parser.parsed_items = [row]

    parser.after_process()

    assert parser.stats.type_corrections == 0


def test_apply_category_falls_back_to_declared_when_unknown() -> None:
    """Не определённый независимо тип — берём заявленный, без пометки расхождения."""
    parser = _classifier_parser(LIGHT_TRUCK)
    row = RowItem({'title': 'Nortec без размера'})

    parser.process_parsed_row(row)

    assert row.vendor.type_production == LIGHT_TRUCK
    assert row.vendor.type_corrected is False
    assert parser.stats.type_corrections == 0
