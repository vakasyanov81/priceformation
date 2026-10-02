"""Тесты типизированных моделей конфигов: разбор, дефолты и валидация."""

from typing import Any

import pytest

from domain.exceptions import ConfigValidationError
from parsers.data_provider import (
    ABSOLUTE_MODE_DELTA,
    ABSOLUTE_MODE_MULTIPLIER,
    AbsoluteMarkUpRules,
    MarkUpRule,
    MarkupRulesConfig,
    VendorConfigEntry,
)

_CONFIG = 'x.json'
_PERCENT = 0.2
_PERCENT_ALT = 0.15
_PREFERRED = 0.1
_RULE_MAX = 50
_ZAPASKA_MIN_RECOMMENDED = 0.08
_ZAPASKA_DELTA = 150
_ZAPASKA_FIRST_MAX = 4999


def _rule(**overrides: Any) -> dict[str, Any]:
    raw: dict[str, Any] = {'min': 0, 'max': _RULE_MAX, 'percent': _PERCENT}
    raw.update(overrides)
    return raw


def _rules(**overrides: Any) -> dict[str, Any]:
    raw: dict[str, Any] = {'markup_rules': {'r': _rule()}}
    raw.update(overrides)
    return raw


# ---------------------------------------------------------------- MarkUpRule


def test_rule_defaults_when_keys_missing() -> None:
    parsed = MarkUpRule.from_dict({}, _CONFIG)

    assert parsed == MarkUpRule(min=0, max=0, percent_markup=0)


def test_rule_accepts_percent_key() -> None:
    parsed = MarkUpRule.from_dict(_rule(), _CONFIG)

    assert parsed == MarkUpRule(min=0, max=_RULE_MAX, percent_markup=_PERCENT)


def test_rule_accepts_percent_markup_key() -> None:
    rule = MarkUpRule.from_dict(_rule(percent_markup=_PERCENT_ALT), _CONFIG)
    assert rule.percent_markup == pytest.approx(_PERCENT_ALT)


def test_rule_prefers_percent_markup() -> None:
    rule = MarkUpRule.from_dict(_rule(percent_markup=_PREFERRED), _CONFIG)
    assert rule.percent_markup == pytest.approx(_PREFERRED)


@pytest.mark.parametrize(
    ('raw', 'place'),
    [
        ({'max': _RULE_MAX, 'percent': 'abc'}, 'x.json → markup_rules.r'),
        ({'max': _RULE_MAX, 'percent': True}, 'x.json → markup_rules.r'),
        ({'min': 'x', 'max': _RULE_MAX, 'percent': _PERCENT}, 'x.json → markup_rules.r'),
    ],
)
def test_rule_number_errors(raw: dict[str, Any], place: str) -> None:
    with pytest.raises(ConfigValidationError, match='должно быть числом') as exc_info:
        MarkUpRule.from_dict(raw, place)
    assert place in str(exc_info.value)


@pytest.mark.parametrize('key', ['percent', 'percent_markup'])
def test_rule_error_names_key_written_by_user(key: str) -> None:
    with pytest.raises(ConfigValidationError, match=f'«{key}» должно быть числом'):
        MarkUpRule.from_dict({key: 'abc'}, _CONFIG)


# ---------------------------------------------------------- AbsoluteMarkUpRules


def test_absolute_defaults() -> None:
    absolute = AbsoluteMarkUpRules.from_dict({}, _CONFIG)
    assert absolute.min_absolute_markup == 0
    assert absolute.markup_percent == 0
    assert absolute.mode == ABSOLUTE_MODE_MULTIPLIER


def test_absolute_reads_mode_and_numbers() -> None:
    absolute = AbsoluteMarkUpRules.from_dict(
        {'min_absolute_markup': _ZAPASKA_DELTA, 'markup_percent': 1.5, 'mode': ABSOLUTE_MODE_DELTA},
        _CONFIG,
    )
    assert absolute == AbsoluteMarkUpRules(
        min_absolute_markup=_ZAPASKA_DELTA,
        markup_percent=1.5,
        mode=ABSOLUTE_MODE_DELTA,
    )


def test_absolute_unknown_mode() -> None:
    with pytest.raises(ConfigValidationError, match='«mode» должен быть'):
        AbsoluteMarkUpRules.from_dict({'mode': 'sum'}, 'x.json → absolute_markup_rules')


def test_absolute_number_error() -> None:
    with pytest.raises(ConfigValidationError, match='«markup_percent» должно быть числом'):
        AbsoluteMarkUpRules.from_dict({'markup_percent': 'x'}, 'x.json → absolute_markup_rules')


# ------------------------------------------------------------ MarkupRulesConfig


def test_optional_keys_default() -> None:
    rules = MarkupRulesConfig.from_dict({}, _CONFIG)
    assert rules.markup_rules == {}
    assert rules.replace_small_recommended is False
    assert rules.min_recommended_percent_markup == 0
    assert rules.max_recommended_percent_markup == 0
    assert rules.absolute_markup_rules.mode == ABSOLUTE_MODE_MULTIPLIER


def test_zero_cap_stays_zero() -> None:
    """Явный 0 в JSON — кап выключен, не fallback 1."""
    rules = MarkupRulesConfig.from_dict(
        {'min_recommended_percent_markup': 0, 'max_recommended_percent_markup': 0},
        _CONFIG,
    )
    assert rules.min_recommended_percent_markup == 0
    assert rules.max_recommended_percent_markup == 0


def test_reads_zapaska_policy_fields() -> None:
    rules = MarkupRulesConfig.from_dict(
        {
            'markup_rules': {'r22': {'min': 0, 'max': _ZAPASKA_FIRST_MAX, 'percent': _PERCENT}},
            'replace_small_recommended': True,
            'min_recommended_percent_markup': _ZAPASKA_MIN_RECOMMENDED,
            'absolute_markup_rules': {'min_absolute_markup': _ZAPASKA_DELTA, 'mode': ABSOLUTE_MODE_DELTA},
        },
        _CONFIG,
    )
    assert rules.replace_small_recommended is True
    assert rules.min_recommended_percent_markup == pytest.approx(_ZAPASKA_MIN_RECOMMENDED)
    assert rules.absolute_markup_rules.min_absolute_markup == _ZAPASKA_DELTA
    assert rules.absolute_markup_rules.mode == ABSOLUTE_MODE_DELTA


def test_reads_nonzero_max_cap_by_exact_key() -> None:
    """Верхний кап читается по точному ключу конфига и не по похожему названию."""
    rules = MarkupRulesConfig.from_dict(
        {'min_recommended_percent_markup': 0.05, 'max_recommended_percent_markup': 0.3},
        _CONFIG,
    )
    assert rules.min_recommended_percent_markup == 0.05
    assert rules.max_recommended_percent_markup == 0.3


def test_ignores_unknown_cap_key() -> None:
    """Ключ с другим именем не подставляется вместо max_recommended_percent_markup."""
    rules = MarkupRulesConfig.from_dict(
        {
            'max_recommended_percent_markup': 0.3,
            'max_recommended_percent_markup_typo': 0.9,
            'MAX_RECOMMENDED_PERCENT_MARKUP': 0.9,
        },
        _CONFIG,
    )
    assert rules.max_recommended_percent_markup == 0.3


def test_markup_rules_must_be_object() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается объект'):
        MarkupRulesConfig.from_dict({'markup_rules': []}, _CONFIG)


def test_absolute_markup_rules_must_be_object() -> None:
    with pytest.raises(ConfigValidationError, match=r'absolute_markup_rules: ожидается объект'):
        MarkupRulesConfig.from_dict({'absolute_markup_rules': 5}, _CONFIG)


def test_rule_entry_must_be_object() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается объект'):
        MarkupRulesConfig.from_dict({'markup_rules': {'r': 'oops'}}, _CONFIG)


def test_replace_small_recommended_must_be_flag() -> None:
    with pytest.raises(ConfigValidationError, match='«replace_small_recommended» должно быть true/false'):
        MarkupRulesConfig.from_dict({'replace_small_recommended': 1}, _CONFIG)


def test_min_recommended_must_be_number() -> None:
    with pytest.raises(ConfigValidationError, match='«min_recommended_percent_markup» должно быть числом'):
        MarkupRulesConfig.from_dict({'min_recommended_percent_markup': '1'}, _CONFIG)


@pytest.mark.parametrize(
    ('price_recommended', 'recommended_is_small', 'replace_small', 'expected'),
    [
        (1000, False, False, False),
        (1000, True, False, False),
        (1000, True, True, True),
        (None, True, False, True),
        (None, False, False, False),
    ],
)
def test_should_replace_with_map(
    price_recommended: float | None,
    recommended_is_small: bool,
    replace_small: bool,
    expected: bool,
) -> None:
    rules = MarkupRulesConfig.from_dict({'replace_small_recommended': replace_small}, _CONFIG)
    assert rules.should_replace_with_map(price_recommended, recommended_is_small) is expected


# ---------------------------------------------------------- VendorConfigEntry


@pytest.mark.parametrize(('enabled', 'expected'), [(0, False), (1, True)])
def test_vendor_entry_reads_enabled(enabled: int, expected: bool) -> None:
    assert VendorConfigEntry.from_dict({'enabled': enabled}, 'stk') == VendorConfigEntry(enabled=expected)


@pytest.mark.parametrize(('enabled', 'expected'), [(True, True), (False, False)])
def test_vendor_entry_reads_json_booleans(enabled: bool, expected: bool) -> None:
    assert VendorConfigEntry.from_dict({'enabled': enabled}, 'stk') == VendorConfigEntry(enabled=expected)


@pytest.mark.parametrize('enabled', [2, -1, 'yes', None, '1', 1.0, 0.0])
def test_vendor_entry_rejects_bad_enabled(enabled: Any) -> None:
    with pytest.raises(ConfigValidationError, match='«enabled» должен быть 0 или 1') as exc_info:
        VendorConfigEntry.from_dict({'enabled': enabled}, 'vendor_list.json → stk')
    assert 'vendor_list.json → stk' in str(exc_info.value)


# --------------------------------- Обёртка: каждое поле протянуто из JSON


def test_markup_rule_reads_all_fields() -> None:
    raw = {'min': 1, 'max': 2, 'percent_markup': 3}
    expected = MarkUpRule(min=1, max=2, percent_markup=3)

    assert MarkUpRule.from_dict(raw, 'x.json') == expected


def test_absolute_markup_rules_reads_all_fields() -> None:
    raw = {'min_absolute_markup': 5, 'markup_percent': 1.5, 'mode': ABSOLUTE_MODE_DELTA}

    assert AbsoluteMarkUpRules.from_dict(raw, 'x.json') == AbsoluteMarkUpRules(
        min_absolute_markup=5,
        markup_percent=1.5,
        mode=ABSOLUTE_MODE_DELTA,
    )


def test_markup_config_reads_all_fields() -> None:
    raw = {
        'markup_rules': {'rule_1': {'min': 1, 'max': 2, 'percent': 0.3}},
        'min_recommended_percent_markup': 0.1,
        'max_recommended_percent_markup': 0.4,
        'absolute_markup_rules': {
            'min_absolute_markup': 5,
            'markup_percent': 1.5,
            'mode': ABSOLUTE_MODE_DELTA,
        },
        'replace_small_recommended': True,
    }

    assert MarkupRulesConfig.from_dict(raw, 'x.json') == MarkupRulesConfig(
        markup_rules={'rule_1': MarkUpRule(min=1, max=2, percent_markup=0.3)},
        min_recommended_percent_markup=0.1,
        max_recommended_percent_markup=0.4,
        absolute_markup_rules=AbsoluteMarkUpRules(
            min_absolute_markup=5,
            markup_percent=1.5,
            mode=ABSOLUTE_MODE_DELTA,
        ),
        replace_small_recommended=True,
    )


def test_vendor_config_entry_reads_all_fields() -> None:
    assert VendorConfigEntry.from_dict({'enabled': 1}, 'x.json') == VendorConfigEntry(enabled=True)
