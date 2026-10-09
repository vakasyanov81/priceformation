"""Реестр стратегий категории: имя из конфига → фабрика."""

import pytest

from domain.exceptions import ConfigValidationError
from parsers.strategies.category import (
    ColumnCanonicalCategory,
    FieldMapCategory,
    FixedCategory,
    HeaderRowsCategory,
    NoCategory,
    TitleKeywordsCategory,
)
from parsers.strategies.registry import make_category_strategy
from parsers.strategies.tire_category import TireSizeCategory
from parsers.vendor_config.slot_configs import CategoryConfig

WHERE = 'mim.json → category'

_KNOWN = [
    ('none', NoCategory),
    ('fixed', FixedCategory),
    ('title_keywords', TitleKeywordsCategory),
    ('field_map', FieldMapCategory),
    ('column_canonical', ColumnCanonicalCategory),
    ('header_rows', HeaderRowsCategory),
    ('tire_size_category', TireSizeCategory),
]


@pytest.mark.parametrize(('name', 'expected_type'), _KNOWN)
def test_make_known_strategy(name: str, expected_type: type) -> None:
    strategy = make_category_strategy(CategoryConfig(strategy=name), WHERE)

    assert isinstance(strategy, expected_type)


def test_fixed_strategy_gets_value_from_config() -> None:
    strategy = make_category_strategy(CategoryConfig(strategy='fixed', fixed_value='Диск'), WHERE)

    assert isinstance(strategy, FixedCategory)


def test_unknown_strategy_raises_with_location() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестная стратегия'):
        make_category_strategy(CategoryConfig(strategy='nope'), WHERE)


def test_unknown_strategy_lists_available_in_message() -> None:
    """Сообщение перечисляет доступные стратегии через ', ', а не подставляет None."""
    with pytest.raises(ConfigValidationError) as exc_info:
        make_category_strategy(CategoryConfig(strategy='nope'), WHERE)

    message = str(exc_info.value)
    assert 'column_canonical, field_map' in message
    assert 'XX' not in message
