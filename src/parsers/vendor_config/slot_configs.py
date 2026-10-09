"""Слоты конфигурации поставщика: категория, заголовок, наценка, поведение."""

from dataclasses import dataclass, field
from typing import Any

from parsers.data_provider.json_fields import as_config_object, read_flag, read_number, read_object
from parsers.data_provider.models import MarkupRulesConfig
from parsers.vendor_config.fields import read_int, read_str_list, read_str_map, read_text

DEFAULT_MIN_REST = 4
DEFAULT_CATEGORY_STRATEGY = 'none'
DEFAULT_TITLE_STRATEGY = 'default'
DEFAULT_POLICY = 'base'
REST_COUNT = 'count'
DEFAULT_PIPELINE = ('title', 'min_rest', 'category', 'markup')


@dataclass(frozen=True, slots=True)
class CategoryConfig:
    """Стратегия категории строки (слот `category`)."""

    strategy: str = DEFAULT_CATEGORY_STRATEGY
    fixed_value: str = ''
    field_name: str = ''
    mapping: dict[str, str] = field(default_factory=dict)
    default_value: str = ''
    unknown_skip: bool = False
    zero_rest_categories: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> CategoryConfig:
        """Разобрать слот `category`: имя стратегии и её параметры."""
        payload = as_config_object(raw, where)
        return cls(
            strategy=read_text(payload, 'strategy', where, DEFAULT_CATEGORY_STRATEGY),
            fixed_value=read_text(payload, 'value', where, ''),
            field_name=read_text(payload, 'field', where, ''),
            mapping=read_str_map(payload, 'map', where),
            default_value=read_text(payload, 'default', where, ''),
            unknown_skip=read_flag(payload, 'unknown_skip', where),
            zero_rest_categories=read_str_list(payload, 'zero_rest_categories', where, ()),
        )


@dataclass(frozen=True, slots=True)
class TitleConfig:
    """Стратегия заголовка строки (слот `title`)."""

    strategy: str = DEFAULT_TITLE_STRATEGY
    variant: str = ''
    aliases: bool = False
    fallback_brand: str = ''

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> TitleConfig:
        """Разобрать слот `title`."""
        payload = as_config_object(raw, where)
        return cls(
            strategy=read_text(payload, 'strategy', where, DEFAULT_TITLE_STRATEGY),
            variant=read_text(payload, 'variant', where, ''),
            aliases=read_flag(payload, 'aliases', where),
            fallback_brand=read_text(payload, 'fallback_brand', where, ''),
        )


@dataclass(frozen=True, slots=True)
class PricingConfig:
    """Наценки поставщика (слот `pricing`).

    `rules` разбирается той же моделью, что и `<supplier>_markup_rules.json`;
    для политики с порогом те же `rules` несут `threshold`/`low`/`high`.
    """

    policy: str = DEFAULT_POLICY
    rules: MarkupRulesConfig = field(default_factory=MarkupRulesConfig)
    threshold: float = 0
    low: float = 0
    high: float = 0

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> PricingConfig:
        """Разобрать слот `pricing`."""
        payload = as_config_object(raw, where)
        rules_payload = read_object(payload, 'rules', where)
        rules_where = f'{where} → rules'
        return cls(
            policy=read_text(payload, 'policy', where, DEFAULT_POLICY),
            rules=MarkupRulesConfig.from_dict(rules_payload, rules_where),
            threshold=read_number(rules_payload, 'threshold', rules_where),
            low=read_number(rules_payload, 'low', rules_where),
            high=read_number(rules_payload, 'high', rules_where),
        )


@dataclass(frozen=True, slots=True)
class BehaviorConfig:
    """Поведение разбора поставщика (секция `behavior`)."""

    min_rest: int = DEFAULT_MIN_REST
    rest: str = REST_COUNT
    skip_markup_without_opt: bool = False
    zero_rest_without_category: bool = False
    collect_missing_recommended: bool = False
    find_manufacturer_on_enrich: bool = True
    pipeline: tuple[str, ...] = DEFAULT_PIPELINE

    @classmethod
    def from_dict(cls, raw: Any, where: str) -> BehaviorConfig:
        """Разобрать секцию `behavior`."""
        payload = as_config_object(raw, where)
        return cls(
            min_rest=read_int(payload, 'min_rest', where, DEFAULT_MIN_REST),
            rest=read_text(payload, 'rest', where, REST_COUNT),
            skip_markup_without_opt=read_flag(payload, 'skip_markup_without_opt', where),
            zero_rest_without_category=read_flag(payload, 'zero_rest_without_category', where),
            collect_missing_recommended=read_flag(payload, 'collect_missing_recommended', where),
            find_manufacturer_on_enrich=read_flag(payload, 'find_manufacturer_on_enrich', where, True),
            pipeline=read_str_list(payload, 'pipeline', where, DEFAULT_PIPELINE),
        )
