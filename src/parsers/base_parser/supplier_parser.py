"""Минимальная граница парсера одной секции для общего оркестратора."""

from typing import Protocol

from domain.product_group_result import ProductGroupResult, ProductPosition
from domain.product_groups import ProductGroup
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.parser_settings import ParserSettings


class SupplierParser(Protocol):
    """Характеристики конкретной модели остаются внутри реализации."""

    settings: ParserSettings
    stats: ParserStats

    @property
    def product_group(self) -> ProductGroup: ...

    def parse(self) -> ProductGroupResult[ProductPosition]: ...
