"""tests for MarkupPolicy numbers and BaseParser.round_price."""

from typing import cast

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.markup_policy import (
    IdentityMarkupPolicy,
    MapOnOptMarkupPolicy,
    MarkupPolicy,
    percent_to_store,
    recommended_percent,
)
from parsers.base_parser.price_markup import get_markup
from parsers.data_provider.markup_rules import AbsoluteMarkUpRules, MarkUpParams, MarkupRules

_OPT = 1000
_OVERLAP_OPT = 5000
_OUT_OF_RANGE_OPT = 20000
_PERCENT = 0.20
_SECOND_PERCENT = 0.19
_RECOMMENDED = 1120
_RECOMMENDED_PERCENT = 0.12
_MIN_RECOMMENDED = 0.14
_MAX_RECOMMENDED = 0.27
_RRC_BELOW_MIN = 1139
_RRC_AT_MIN = 1140
_RRC_AT_MAX = 1270
_RRC_ABOVE_MAX = 1271
_MIN_ABSOLUTE = 300
_ABSOLUTE_PERCENT = 1.5
_SELLING_AT_FLOOR = 1300
_SELLING_BELOW_FLOOR = 1299
_ABSOLUTE_PRICE = 1500
_APPLY_MIN_RECOMMENDED = 0.15
_APPLY_ABSOLUTE_PERCENT = 1.3
_APPLY_MAX_ON = 0.10
_RRC_OK = 2000
_RRC_LOW_MARGIN = 1100
_ZERO = 0
_ROUND_UP_PRICE = 1121
_ROUNDED_UP_PRICE = 1130
_ROUND_EXACT_PRICE = 1120
_FIRST_RULE = MarkUpParams(min=0, max=5001, percent_markup=_PERCENT)
_SECOND_RULE = MarkUpParams(min=5000, max=10001, percent_markup=_SECOND_PERCENT)
_OVERLAP_MAP = (_FIRST_RULE, _SECOND_RULE)
_MAP_OPT = 100
_MAP_PERCENT = 0.7
_MAP_PRICE = 170
_MAP_RULE = MarkUpParams(min=0, max=201, percent_markup=_MAP_PERCENT)
_IGNORED_RRC = 9999
_MAP_STORED_PERCENT = 70
_IDENTITY_OPT = 1234.56
_IDENTITY_RRC = 2000


def _policy(
    price_map: tuple[MarkUpParams, ...],
    *,
    min_recommended: float = 0,
    max_recommended: float = 0,
    min_absolute: float = 0,
    absolute_percent: float = 0,
    policy_cls: type[MarkupPolicy] = MarkupPolicy,
) -> MarkupPolicy:
    rules = MarkupRules(
        markup_rules={},
        min_recommended_percent_markup=min_recommended,
        max_recommended_percent_markup=max_recommended,
        absolute_markup_rules=AbsoluteMarkUpRules(
            min_absolute_markup=min_absolute,
            markup_percent=absolute_percent,
        ),
    )
    return policy_cls(rules, price_map)


def _map_on_opt_policy() -> MapOnOptMarkupPolicy:
    return cast(
        MapOnOptMarkupPolicy,
        _policy(
            (_MAP_RULE,),
            min_recommended=_APPLY_MIN_RECOMMENDED,
            min_absolute=_MIN_ABSOLUTE,
            absolute_percent=_APPLY_ABSOLUTE_PERCENT,
            policy_cls=MapOnOptMarkupPolicy,
        ),
    )


def _mim_policy() -> MarkupPolicy:
    return _policy(
        (_FIRST_RULE,),
        min_recommended=_MIN_RECOMMENDED,
        max_recommended=_MAX_RECOMMENDED,
        min_absolute=_MIN_ABSOLUTE,
        absolute_percent=_ABSOLUTE_PERCENT,
    )


def _apply_policy(
    *,
    min_recommended: float = _APPLY_MIN_RECOMMENDED,
    max_recommended: float = 0,
    min_absolute: float = 0,
    absolute_percent: float = _APPLY_ABSOLUTE_PERCENT,
) -> MarkupPolicy:
    return _policy(
        (_FIRST_RULE,),
        min_recommended=min_recommended,
        max_recommended=max_recommended,
        min_absolute=min_absolute,
        absolute_percent=absolute_percent,
    )


def test_markup_percent_for_opt_in_range() -> None:
    assert _policy((_FIRST_RULE,)).markup_percent_for_opt(_OPT) == _PERCENT


def test_markup_percent_for_opt_empty_map() -> None:
    assert _policy(()).markup_percent_for_opt(_OPT) == _ZERO


def test_markup_percent_for_opt_first_rule_wins() -> None:
    assert _policy(_OVERLAP_MAP).markup_percent_for_opt(_OVERLAP_OPT) == _PERCENT


def test_markup_percent_for_opt_boundary_min() -> None:
    assert _policy((_SECOND_RULE,)).markup_percent_for_opt(_SECOND_RULE.min) == _SECOND_PERCENT


def test_markup_percent_for_opt_boundary_max() -> None:
    assert _policy((_SECOND_RULE,)).markup_percent_for_opt(_SECOND_RULE.max) == _SECOND_PERCENT


def test_markup_percent_for_opt_out_of_range() -> None:
    assert _policy(_OVERLAP_MAP).markup_percent_for_opt(_OUT_OF_RANGE_OPT) == _SECOND_PERCENT


def test_markup_percent_for_opt_zero() -> None:
    assert _policy(_OVERLAP_MAP).markup_percent_for_opt(_ZERO) == _SECOND_PERCENT


def test_recommended_percent_without_rrc_is_zero() -> None:
    assert recommended_percent(_OPT, None) == _ZERO


def test_recommended_percent_from_rrc() -> None:
    assert recommended_percent(_OPT, _RECOMMENDED) == _RECOMMENDED_PERCENT


def test_is_small_recommended_percent_below_min() -> None:
    policy = _policy((_FIRST_RULE,), min_recommended=_MIN_RECOMMENDED)
    assert policy._is_small_recommended_percent(_OPT, _RRC_BELOW_MIN) is True  # noqa: WPS437


def test_small_rrc_percent_at_min() -> None:
    policy = _policy((_FIRST_RULE,), min_recommended=_MIN_RECOMMENDED)
    assert policy._is_small_recommended_percent(_OPT, _RRC_AT_MIN) is False  # noqa: WPS437


def test_is_big_recommended_percent_above_max() -> None:
    assert _mim_policy()._is_big_recommended_percent(_OPT, _RRC_ABOVE_MAX) is True  # noqa: WPS437


def test_big_rrc_percent_at_max() -> None:
    assert _mim_policy()._is_big_recommended_percent(_OPT, _RRC_AT_MAX) is False  # noqa: WPS437


def test_big_rrc_percent_max_off() -> None:
    policy = _policy((_FIRST_RULE,), max_recommended=_ZERO)
    assert policy._is_big_recommended_percent(_OPT, _RECOMMENDED) is False  # noqa: WPS437


def test_is_small_absolute_markup_below_floor() -> None:
    assert _mim_policy()._is_small_absolute_markup(_SELLING_BELOW_FLOOR, _OPT) is True  # noqa: WPS437


def test_small_absolute_at_floor() -> None:
    assert _mim_policy()._is_small_absolute_markup(_SELLING_AT_FLOOR, _OPT) is False  # noqa: WPS437


def test_price_with_absolute_rule() -> None:
    assert _mim_policy()._price_with_absolute_rule(_OPT) == _ABSOLUTE_PRICE  # noqa: WPS437


def test_apply_no_rrc_uses_map() -> None:
    assert _apply_policy().apply(_OPT, None) == get_markup(_OPT, _PERCENT)


def test_apply_keeps_rrc() -> None:
    policy = _apply_policy(min_absolute=_MIN_ABSOLUTE)
    assert policy.apply(_OPT, _RRC_OK) == _RRC_OK


def test_apply_rrc_hits_floor() -> None:
    policy = _apply_policy(min_absolute=_MIN_ABSOLUTE)
    assert policy.apply(_OPT, _RRC_LOW_MARGIN) == _OPT * _APPLY_ABSOLUTE_PERCENT


def test_apply_rrc_at_floor() -> None:
    policy = _apply_policy(min_absolute=_MIN_ABSOLUTE)
    assert policy.apply(_OPT, _SELLING_AT_FLOOR) == _SELLING_AT_FLOOR


def test_apply_max_off_uses_map() -> None:
    policy = _apply_policy(max_recommended=_ZERO)
    assert policy.apply(_OPT, None) == get_markup(_OPT, _PERCENT)


def test_apply_max_on_no_rrc_uses_map() -> None:
    policy = _apply_policy(max_recommended=_APPLY_MAX_ON)
    assert policy.apply(_OPT, None) == get_markup(_OPT, _PERCENT)


def test_map_on_opt_apply_in_range() -> None:
    assert _map_on_opt_policy().apply(_MAP_OPT, None) == _MAP_PRICE


def test_map_on_opt_apply_ignores_recommended() -> None:
    assert _map_on_opt_policy().apply(_MAP_OPT, _IGNORED_RRC) == _MAP_PRICE


def test_map_on_opt_apply_ignores_absolute() -> None:
    mim = _policy(
        (_MAP_RULE,),
        min_recommended=_APPLY_MIN_RECOMMENDED,
        min_absolute=_MIN_ABSOLUTE,
        absolute_percent=_APPLY_ABSOLUTE_PERCENT,
    )
    assert mim.apply(_MAP_OPT, None) == _MAP_OPT * _APPLY_ABSOLUTE_PERCENT
    assert _map_on_opt_policy().apply(_MAP_OPT, None) == _MAP_PRICE


def test_map_on_opt_apply_zero_opt() -> None:
    assert _map_on_opt_policy().apply(_ZERO, None) == _ZERO


def test_map_on_opt_apply_empty_map() -> None:
    policy = _policy((), policy_cls=MapOnOptMarkupPolicy)
    assert policy.apply(_MAP_OPT, None) == _MAP_OPT


def test_percent_to_store_mim_is_none() -> None:
    assert percent_to_store(_apply_policy(), _OPT) is None


def test_percent_to_store_map_on_opt() -> None:
    assert percent_to_store(_map_on_opt_policy(), _MAP_OPT) == _MAP_STORED_PERCENT


def test_map_on_opt_stored_percent_markup() -> None:
    assert _map_on_opt_policy().stored_percent_markup(_MAP_OPT) == _MAP_STORED_PERCENT


def test_map_on_opt_stored_percent_empty_map() -> None:
    policy = _policy((), policy_cls=MapOnOptMarkupPolicy)
    assert percent_to_store(policy, _MAP_OPT) == _ZERO


def test_round_price_up() -> None:
    assert BaseParser.round_price(_ROUND_UP_PRICE) == _ROUNDED_UP_PRICE


def test_round_price_exact() -> None:
    assert BaseParser.round_price(_ROUND_EXACT_PRICE) == _ROUND_EXACT_PRICE


def test_identity_apply_keeps_opt() -> None:
    assert IdentityMarkupPolicy.create().apply(_IDENTITY_OPT, _IDENTITY_RRC) == _IDENTITY_OPT


def test_identity_apply_zero_opt() -> None:
    assert IdentityMarkupPolicy.create().apply(_ZERO, _IDENTITY_RRC) == _ZERO


def test_percent_to_store_identity_is_none() -> None:
    assert percent_to_store(IdentityMarkupPolicy.create(), _IDENTITY_OPT) is None
