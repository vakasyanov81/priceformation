"""Реестр стратегий rest: имя из конфига → правило остатка."""

import pytest

from domain.exceptions import ConfigValidationError
from domain.row_item.row_item import RowItem
from parsers.strategies.rest import CountRest, MinusReserveRest
from parsers.strategies.rest_registry import make_rest_strategy
from parsers.vendor_config.slot_configs import BehaviorConfig

WHERE = 'pioner.json → behavior'

_KNOWN = [('count', CountRest), ('minus_reserve', MinusReserveRest)]


@pytest.mark.parametrize(('name', 'expected_type'), _KNOWN)
def test_make_known_rest_strategy(name: str, expected_type: type) -> None:
    strategy = make_rest_strategy(BehaviorConfig(rest=name), WHERE)

    assert isinstance(strategy, expected_type)


def test_count_returns_rest_as_is() -> None:
    row = RowItem({'rest_count': 7, 'reserve_count': 2})

    assert CountRest().item_rest(row) == 7


def test_minus_reserve_subtracts_reserve() -> None:
    row = RowItem({'rest_count': 7, 'reserve_count': 2})

    assert MinusReserveRest().item_rest(row) == 5


def test_minus_reserve_without_counts() -> None:
    assert MinusReserveRest().item_rest(RowItem({})) == 0


def test_unknown_rest_raises_with_location() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестная стратегия rest'):
        make_rest_strategy(BehaviorConfig(rest='nope'), WHERE)
