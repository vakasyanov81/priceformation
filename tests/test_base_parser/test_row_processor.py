"""Тесты пошаговой обработки строки: наценка и минимальный остаток."""

from domain.row_item.row_item import RowItem
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MapOnOptMarkupPolicy,
    MarkupPolicy,
)
from parsers.base_parser.row_processor import RowProcessor, apply_min_rest
from parsers.data_provider import AbsoluteMarkUpRules, MarkUpRule, MarkupRulesConfig

_OPT = 1000
_RRC = 2000
_MIN_RECOMMENDED = 0.15
_PERCENT = 0.2
_UNROUNDED_OPT = 1001
_ROUNDED_PRICE = 1210
_MIN_REST = 4
_REST_AT_MIN = 4
_REST_BELOW = 3

_RULE = MarkUpRule(min=0, max=5001, percent_markup=_PERCENT)

_LOW = MarkUpRule(min=0, max=0, percent_markup=0.2)
_MID = MarkUpRule(min=1, max=10, percent_markup=0.5)
_HIGH = MarkUpRule(min=11, max=30, percent_markup=0.6)
_MAP = (_LOW, _MID, _HIGH)
_HIGH_OPT = 25
_HIGH_PERCENT = 60


def _rules(*, min_recommended: float = 0) -> MarkupRulesConfig:
    return MarkupRulesConfig(
        markup_rules={},
        min_recommended_percent_markup=min_recommended,
        absolute_markup_rules=AbsoluteMarkUpRules(),
    )


def _map_on_opt() -> MapOnOptMarkupPolicy:
    return MapOnOptMarkupPolicy(_rules(), _MAP)


def test_add_price_markup_zero_opt_identity_keeps_zero() -> None:
    """Нулевой закуп у «без наценки» остаётся нулём, а не единицей."""
    row = RowItem({'price_opt': 0})
    RowProcessor(markup_policy=IdentityMarkupPolicy.create()).add_price_markup(row)
    assert row.pricing.price_markup == 0


def test_add_price_markup_keeps_recommended_price() -> None:
    """РРЦ доходит до policy.apply, а не подменяется None."""
    policy = MarkupPolicy(_rules(min_recommended=_MIN_RECOMMENDED), (_RULE,))
    row = RowItem({'price_opt': _OPT, 'price_recommended': _RRC})
    RowProcessor(markup_policy=policy).add_price_markup(row)
    assert row.pricing.price_markup == _RRC


def test_add_price_markup_rounds_up_to_ten() -> None:
    """Наценка округляется вверх до десятков (целочисленное деление)."""
    policy = MarkupPolicy(_rules(min_recommended=_MIN_RECOMMENDED), (_RULE,))
    row = RowItem({'price_opt': _UNROUNDED_OPT})
    RowProcessor(markup_policy=policy).add_price_markup(row)
    assert row.pricing.price_markup == _ROUNDED_PRICE


def test_add_price_markup_stores_percent_for_opt_price() -> None:
    """Процент в строке считается от реального закупа, а не от None."""
    row = RowItem({'price_opt': _HIGH_OPT})
    RowProcessor(markup_policy=_map_on_opt()).add_price_markup(row)
    assert row.pricing.percent_markup == _HIGH_PERCENT
    assert row.pricing.price_markup == _HIGH_OPT * (1 + _HIGH.percent_markup)


def test_get_markup_percent_uses_price_argument() -> None:
    """get_markup_percent не подменяет цену на None."""
    processor = RowProcessor(markup_policy=_map_on_opt())
    assert processor.get_markup_percent(_MID.min) == _MID.percent_markup


def test_apply_min_rest_keeps_rest_equal_to_min() -> None:
    """Остаток, равный минимуму, не обнуляется (строго меньше)."""
    row = RowItem({'rest_count': _REST_AT_MIN})
    apply_min_rest(row, _REST_AT_MIN, _MIN_REST)
    assert row.stock.rest_count == _REST_AT_MIN


def test_apply_min_rest_zeroes_below_min() -> None:
    row = RowItem({'rest_count': _REST_BELOW})
    apply_min_rest(row, _REST_BELOW, _MIN_REST)
    assert row.stock.rest_count == 0


def test_apply_min_rest_zeroes_none() -> None:
    row = RowItem({'rest_count': 10})
    apply_min_rest(row, None, _MIN_REST)
    assert row.stock.rest_count == 0
