"""Фабрика config-driven парсера из конфига поставщика (этап 3).

Собирает ``StrategyHooks`` из ``VendorSection``, строит ``ParserParams``
и ``MarkupPolicy`` из конфига, и возвращает ``BaseParser``, готовый к разбору.
"""

from __future__ import annotations

from typing import Any

from domain.protocols import ConfigProvider
from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.file_reader import data_reader_for
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.base_parser.row_processor import RowProcessor
from parsers.base_parser.strategy_hooks import StrategyHooks, warehouse_filter_for
from parsers.strategies.category_fields import CategoryFields
from parsers.strategies.pricing_registry import make_pricing_strategy
from parsers.strategies.product_type import ProductTypeClassifier
from parsers.strategies.registry import make_category_strategy
from parsers.strategies.rest_registry import make_rest_strategy
from parsers.strategies.title_registry import make_title_strategy
from parsers.vendor_config.models import VendorConfig, VendorSection
from parsers.vendor_config.slot_configs import BehaviorConfig


def parser_params_from_section(section: VendorSection, folder: str) -> ParserParams:
    """Собрать ``ParserParams`` из секции конфига.

    Args:
        section: Секция поставщика (один лист/файл).
        folder: Имя папки поставщика (``file_prices/<folder>/``).
    """
    return ParserParams(
        supplier=ParseParamsSupplier(folder_name=folder, name=section.name, code=section.id),
        start_row=section.start_row,
        sheet_info=section.sheet_info,
        columns=dict(section.columns.items()),
        stop_words=(),
        file_templates=section.file_templates,
        sheet_indexes=section.sheet_indexes,
        row_item_adaptor=RowItem,
    )


def vendor_markup_policy_from_config(section: VendorSection) -> MarkupPolicy:
    """Собрать политику наценки из слота ``pricing`` секции."""
    return make_pricing_strategy(section.pricing, 'section.pricing')


def strategy_hooks_from_section(
    section: VendorSection,
    behavior: BehaviorConfig,
    config_provider: ConfigProvider,
    folder: str = '',
) -> StrategyHooks:
    """Собрать ``StrategyHooks`` из секции и поведения поставщика.

    Args:
        section: Секция поставщика.
        behavior: Поведение поставщика (из ``VendorConfig.behavior``).
        config_provider: Провайдер путей окружения (список складов поставщика).
        folder: Папка поставщика; нужна для фильтра складов по городу (``warehouse_cities``).
    """
    category_strategy = make_category_strategy(section.category, f'section {section.id} category')
    manufacturer_reader = getattr(category_strategy, 'current_manufacturer', None)
    return StrategyHooks(
        category=category_strategy,
        title=make_title_strategy(
            section.title,
            f'section {section.id} title',
            manufacturer_reader=manufacturer_reader,
            config_provider=config_provider,
        ),
        rest=make_rest_strategy(behavior, f'section {section.id} rest'),
        category_fields=_category_fields(section),
        product_type=_product_type(section),
        min_rest=behavior.min_rest,
        find_manufacturer_on_enrich=behavior.find_manufacturer_on_enrich,
        zero_rest_without_category=behavior.zero_rest_without_category,
        pipeline=behavior.pipeline,
        warehouse_filter=warehouse_filter_for(behavior, folder, config_provider),
        order_from_warehouse_name=behavior.order_from_warehouse_name,
    )


def _category_fields(section: VendorSection) -> CategoryFields | None:
    """Стратегия полей по категории-размеру из слота `category`, если задана."""
    if not section.category.size_fields:
        return None
    return CategoryFields(section.category.size_fields)


def _product_type(section: VendorSection) -> ProductTypeClassifier | None:
    """Независимый классификатор типа, если включён `category.calculate_type`."""
    if not section.category.calculate_type:
        return None
    return ProductTypeClassifier()


def make_config_driven_parser(
    section: VendorSection,
    vendor_config: VendorConfig,
    parse_config: ParseConfiguration,
) -> BaseParser:
    """Собрать ``BaseParser`` с поведением из конфига поставщика.

    Args:
        section: Секция поставщика (один лист/файл).
        vendor_config: Весь конфиг поставщика (нужен для ``behavior`` и ``reader``).
        parse_config: ``ParseConfiguration`` с провайдерами данных.

    Returns:
        ``BaseParser`` с инжектированными стратегиями.
    """
    hooks = strategy_hooks_from_section(
        section, vendor_config.behavior, parse_config.config_provider, vendor_config.folder
    )
    policy = vendor_markup_policy_from_config(section)
    data_reader: type[Any] = data_reader_for(vendor_config.reader)
    return BaseParser(
        parse_config=parse_config,
        row_processor=RowProcessor(markup_policy=policy),
        strategy_hooks=hooks,
        data_reader=data_reader,
    )
