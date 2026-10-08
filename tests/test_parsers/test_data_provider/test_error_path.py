"""Сообщения об ошибках моделей наценок содержат полный путь до ключа.

Дополнительно закрепляет допустимые режимы `mode`: список режимов входит
в текст ошибки и не должен подменяться.
"""

from typing import Any

import pytest

from domain.exceptions import ConfigValidationError
from parsers.data_provider.models import (
    ABSOLUTE_MODE_DELTA,
    ABSOLUTE_MODE_MULTIPLIER,
    AbsoluteMarkUpRules,
    MarkUpRule,
    MarkupRulesConfig,
    VendorConfigEntry,
)

WHERE = 'x.json'
RULE_PLACE = 'x.json → markup_rules.r'
ABSOLUTE_PLACE = 'x.json → absolute_markup_rules'
ALLOWED_MODES = f'{ABSOLUTE_MODE_MULTIPLIER} или {ABSOLUTE_MODE_DELTA}'


def test_rules_root_must_be_object_with_path() -> None:
    """Корень `<supplier>_markup_rules.json` без пути — мутант `where → None`."""
    with pytest.raises(ConfigValidationError) as exc_info:
        MarkupRulesConfig.from_dict([], WHERE)

    assert str(exc_info.value).startswith(WHERE)


def test_rule_root_must_be_object_with_path() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        MarkUpRule.from_dict([], RULE_PLACE)

    assert str(exc_info.value).startswith(RULE_PLACE)


def test_absolute_root_must_be_object_with_path() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        AbsoluteMarkUpRules.from_dict([], ABSOLUTE_PLACE)

    assert str(exc_info.value).startswith(ABSOLUTE_PLACE)


def test_vendor_entry_root_must_be_object_with_path() -> None:
    with pytest.raises(ConfigValidationError) as exc_info:
        VendorConfigEntry.from_dict([], WHERE)

    assert str(exc_info.value).startswith(WHERE)


PATH_CASES = [
    ({'min_recommended_percent_markup': 'x'}, WHERE),
    ({'max_recommended_percent_markup': 'x'}, WHERE),
    ({'replace_small_recommended': 1}, WHERE),
    ({'markup_rules': 'x'}, f'{WHERE} → markup_rules'),
    ({'markup_rules': {'r': 'x'}}, f'{WHERE} → markup_rules'),
    ({'markup_rules': {'r': {'max': 'x'}}}, f'{WHERE} → markup_rules.r'),
    ({'absolute_markup_rules': 'x'}, ABSOLUTE_PLACE),
    ({'absolute_markup_rules': {'min_absolute_markup': 'x'}}, ABSOLUTE_PLACE),
    ({'absolute_markup_rules': {'markup_percent': 'x'}}, ABSOLUTE_PLACE),
    ({'absolute_markup_rules': {'mode': 'bad'}}, ABSOLUTE_PLACE),
]


@pytest.mark.parametrize(('raw', 'path'), PATH_CASES, ids=range(len(PATH_CASES)))
def test_error_message_contains_full_path(raw: dict[str, Any], path: str) -> None:
    """Путь до ключа — в каждой ошибке разбора, включая вложенные секции."""
    with pytest.raises(ConfigValidationError) as exc_info:
        MarkupRulesConfig.from_dict(raw, WHERE)

    assert path in str(exc_info.value)


def test_rule_number_error_contains_full_path() -> None:
    """Правило наценки: путь до `max` — отдельного теста в общей параметризации нет."""
    with pytest.raises(ConfigValidationError) as exc_info:
        MarkUpRule.from_dict({'min': 0, 'max': 'x'}, RULE_PLACE)

    assert RULE_PLACE in str(exc_info.value)


def test_mode_error_lists_allowed_modes() -> None:
    """Режимы `mode` перечислены в ошибке: не список режимов — уже не подсказка."""
    with pytest.raises(ConfigValidationError) as exc_info:
        AbsoluteMarkUpRules.from_dict({'mode': 'bad'}, ABSOLUTE_PLACE)

    assert ALLOWED_MODES in str(exc_info.value)
    assert ABSOLUTE_PLACE in str(exc_info.value)
