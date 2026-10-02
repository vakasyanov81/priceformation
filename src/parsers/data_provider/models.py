"""
типизированные формы пользовательских конфигов
"""

from dataclasses import dataclass, field
from typing import Any

from parsers.data_provider.json_fields import (
    RawConfig,
    as_config_object,
    read_flag,
    read_mode,
    read_number,
    read_object,
    read_zero_one_flag,
)

ABSOLUTE_MODE_MULTIPLIER = 'multiplier'
ABSOLUTE_MODE_DELTA = 'delta'
_ABSOLUTE_MODES = (ABSOLUTE_MODE_MULTIPLIER, ABSOLUTE_MODE_DELTA)
_MARKUP_RULES_KEY = 'markup_rules'
_ABSOLUTE_RULES_KEY = 'absolute_markup_rules'
_PERCENT_KEY = 'percent_markup'
_PERCENT_ALIAS_KEY = 'percent'


def _percent_key(rule: RawConfig) -> str:
    """Ключ процента наценки в JSON: `percent_markup`, иначе совместимый алиас `percent`."""
    if _PERCENT_ALIAS_KEY in rule and _PERCENT_KEY not in rule:
        return _PERCENT_ALIAS_KEY
    return _PERCENT_KEY


@dataclass(frozen=True, slots=True)
class MarkUpRule:
    """Правило наценки на диапазон цен."""

    min: float
    max: float
    percent_markup: float

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> MarkUpRule:
        """Разобрать правило. Принимает `percent` или `percent_markup`."""
        rule = as_config_object(raw, where)
        return cls(
            min=read_number(rule, 'min', where),
            max=read_number(rule, 'max', where),
            percent_markup=read_number(rule, _percent_key(rule), where),
        )


@dataclass(frozen=True, slots=True)
class AbsoluteMarkUpRules:
    """Абсолютные правила наценки."""

    min_absolute_markup: float = 0
    markup_percent: float = 0
    mode: str = ABSOLUTE_MODE_MULTIPLIER

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> AbsoluteMarkUpRules:
        """Разобрать секцию `absolute_markup_rules`."""
        absolute = as_config_object(raw, where)
        return cls(
            min_absolute_markup=read_number(absolute, 'min_absolute_markup', where),
            markup_percent=read_number(absolute, 'markup_percent', where),
            mode=read_mode(absolute, where, _ABSOLUTE_MODES),
        )


@dataclass(frozen=True, slots=True)
class MarkupRulesConfig:
    """Наценки поставщика целиком (`<supplier>_markup_rules.json`)."""

    markup_rules: dict[str, MarkUpRule] = field(default_factory=dict)
    min_recommended_percent_markup: float = 0
    max_recommended_percent_markup: float = 0
    absolute_markup_rules: AbsoluteMarkUpRules = field(default_factory=AbsoluteMarkUpRules)
    replace_small_recommended: bool = False

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> MarkupRulesConfig:
        """Разобрать `<supplier>_markup_rules.json`."""
        rules = as_config_object(raw, where)
        return cls(
            markup_rules=cls._read_rules(read_object(rules, _MARKUP_RULES_KEY, where), where),
            min_recommended_percent_markup=read_number(rules, 'min_recommended_percent_markup', where),
            max_recommended_percent_markup=read_number(rules, 'max_recommended_percent_markup', where),
            absolute_markup_rules=AbsoluteMarkUpRules.from_dict(
                read_object(rules, _ABSOLUTE_RULES_KEY, where),
                f'{where} → {_ABSOLUTE_RULES_KEY}',
            ),
            replace_small_recommended=read_flag(rules, 'replace_small_recommended', where),
        )

    @classmethod
    def _read_rules(cls, rules_raw: RawConfig, where: str) -> dict[str, MarkUpRule]:
        """Разобрать секцию `markup_rules`: имя правила → правило на ценовой диапазон."""
        parsed: dict[str, MarkUpRule] = {}
        for name, rule_raw in rules_raw.items():
            parsed[name] = MarkUpRule.from_dict(rule_raw, f'{where} → {_MARKUP_RULES_KEY}.{name}')
        return parsed

    def should_replace_with_map(self, price_recommended: float | None, recommended_is_small: bool) -> bool:
        """Мими держит РРЦ, если он есть; запаска всё равно проверяет min-%."""
        if price_recommended and not self.replace_small_recommended:
            return False
        return recommended_is_small


@dataclass(frozen=True, slots=True)
class VendorConfigEntry:
    """Запись поставщика в `vendor_list.json`."""

    enabled: bool

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> VendorConfigEntry:
        """Разобрать запись поставщика (в JSON `enabled` — 0 или 1)."""
        vendor = as_config_object(raw, where)
        return cls(enabled=read_zero_one_flag(vendor, 'enabled', where))
