"""Фабрика config-driven парсера из конфига поставщика (этап 3).

Собирает ``StrategyHooks`` из ``VendorSection``, строит ``ParserParams``
и ``MarkupPolicy`` из конфига, и возвращает ``BaseParser``, готовый к разбору.
"""

from __future__ import annotations

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_config import (
    ParseConfiguration,
    ParseParamsSupplier,
    ParserParams,
)
from parsers.base_parser.markup_policy import MarkupPolicy
from parsers.base_parser.row_processor import RowProcessor
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.strategies.pricing_registry import make_pricing_strategy
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


def strategy_hooks_from_section(section: VendorSection, behavior: BehaviorConfig) -> StrategyHooks:
    """Собрать ``StrategyHooks`` из секции и поведения поставщика.

    Args:
        section: Секция поставщика.
        behavior: Поведение поставщика (из ``VendorConfig.behavior``).
    """
    return StrategyHooks(
        category=make_category_strategy(section.category, f'section {section.id} category'),
        title=make_title_strategy(
            section.title,
            f'section {section.id} title',
            manufacturer_reader=lambda: None,
        ),
        rest=make_rest_strategy(behavior, f'section {section.id} rest'),
        min_rest=behavior.min_rest,
        find_manufacturer_on_enrich=behavior.find_manufacturer_on_enrich,
        pipeline=behavior.pipeline,
    )


def make_config_driven_parser(
    section: VendorSection,
    vendor_config: VendorConfig,
    parse_config: ParseConfiguration,  # noqa: WPS110
) -> BaseParser:
    """Собрать ``BaseParser`` с поведением из конфига поставщика.

    Args:
        section: Секция поставщика (один лист/файл).
        vendor_config: Весь конфиг поставщика (нужен для ``behavior``).
        parse_config: ``ParseConfiguration`` с провайдерами данных.

    Returns:
        ``BaseParser`` с инжектированными стратегиями.
    """
    hooks = strategy_hooks_from_section(section, vendor_config.behavior)
    policy = vendor_markup_policy_from_config(section)
    return BaseParser(
        parse_config=parse_config,
        row_processor=RowProcessor(markup_policy=policy),
        strategy_hooks=hooks,
    )
