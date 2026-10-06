"""
Реестр стратегий слота `category`: имя из конфига → фабрика стратегии.
"""

from __future__ import annotations

from collections.abc import Callable

from domain.exceptions import ConfigValidationError
from parsers.strategies.category import (
    ColumnCanonicalCategory,
    FieldMapCategory,
    FixedCategory,
    HeaderRowsCategory,
    NoCategory,
    TitleKeywordsCategory,
)
from parsers.strategies.protocols import CategoryStrategy
from parsers.vendor_config.slot_configs import CategoryConfig

_CATEGORY_FACTORIES: dict[str, Callable[[CategoryConfig], CategoryStrategy]] = {
    'none': NoCategory.from_config,
    'fixed': FixedCategory.from_config,
    'title_keywords': TitleKeywordsCategory.from_config,
    'field_map': FieldMapCategory.from_config,
    'column_canonical': ColumnCanonicalCategory.from_config,
    'header_rows': HeaderRowsCategory.from_config,
}


def make_category_strategy(config: CategoryConfig, where: str) -> CategoryStrategy:
    """Собрать стратегию категории по имени из конфига."""
    factory = _CATEGORY_FACTORIES.get(config.strategy)
    if factory is None:
        available = ', '.join(sorted(_CATEGORY_FACTORIES))
        raise ConfigValidationError(
            f'{where}: неизвестная стратегия категории {config.strategy!r} (доступны: {available})',
        )
    return factory(config)
