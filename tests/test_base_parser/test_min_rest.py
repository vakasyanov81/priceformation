"""RowFilters.skip_by_min_rest: дефолтный остаток и стратегия из хуков — без BaseParser."""

from unittest.mock import MagicMock

import pytest

from domain.row_item.row_item import RowItem
from parsers.base_parser.row_filters import DEFAULT_MIN_REST, RowFilters
from parsers.base_parser.strategy_hooks import StrategyHooks

_STRATEGY_MIN_REST = 10
_STRATEGY_REST = 7


@pytest.mark.parametrize(
    ('rest', 'expected'),
    [(DEFAULT_MIN_REST - 1, 0), (DEFAULT_MIN_REST, DEFAULT_MIN_REST)],
)
def test_default_uses_row_rest_and_default_min_rest(rest: int, expected: int) -> None:
    row = RowItem({'rest_count': rest})

    RowFilters().skip_by_min_rest(row)

    assert row.stock.rest_count == expected


def test_hooks_without_rest_strategy_use_defaults() -> None:
    row = RowItem({'rest_count': DEFAULT_MIN_REST - 1})

    RowFilters(StrategyHooks(min_rest=1)).skip_by_min_rest(row)

    assert row.stock.rest_count == 0


def test_rest_strategy_overrides_row_rest_and_min_rest() -> None:
    strategy = MagicMock()
    strategy.item_rest.return_value = _STRATEGY_REST
    row = RowItem({'rest_count': 100})

    RowFilters(StrategyHooks(rest=strategy, min_rest=_STRATEGY_MIN_REST)).skip_by_min_rest(row)

    assert row.stock.rest_count == 0
