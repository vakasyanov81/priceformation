"""Разбор конфига поставщика: наследование секций, слоты и валидация."""

from typing import Any

import pytest

from domain.exceptions import ConfigValidationError
from parsers.data_provider.models import ABSOLUTE_MODE_DELTA, AbsoluteMarkUpRules, MarkUpRule, MarkupRulesConfig
from parsers.vendor_config.models import VendorConfig, VendorSection
from parsers.vendor_config.slot_configs import (
    DEFAULT_PIPELINE,
    BehaviorConfig,
    CategoryConfig,
    PricingConfig,
    TitleConfig,
)

FOLDER = 'mim'
WHERE = 'mim.json'

MINIMAL: dict[str, Any] = {
    'enabled': 1,
    'code': 'mim',
    'name': 'Мим',
    'start_row': 2,
    'file_templates': ['*.xls'],
    'sections': [{'columns': {'1': 'manufacturer_name'}}],
}


def _config(**overrides: Any) -> VendorConfig:
    raw = {**MINIMAL, **overrides}
    return VendorConfig.from_dict(raw, FOLDER, WHERE)


def test_vendor_fields_parsed() -> None:
    config = _config()

    assert config.folder == FOLDER
    assert config.enabled is True
    assert config.code == 'mim'
    assert config.name == 'Мим'
    assert config.start_row == 2
    assert config.file_templates == ('*.xls',)
    assert config.reader == 'xls'


def test_section_inherits_vendor_fields() -> None:
    section = _config().sections[0]

    assert section.id == 'mim'
    assert section.name == 'Мим'
    assert section.start_row == 2
    assert section.file_templates == ('*.xls',)
    assert section.columns == {1: 'manufacturer_name'}


def test_xls_columns_get_integer_keys() -> None:
    sections = [{'columns': {'1': 'manufacturer_name'}}]
    config = _config(columns={'2': 'title'}, sections=sections)

    assert config.columns == {2: 'title'}
    assert config.sections[0].columns == {1: 'manufacturer_name'}


def test_json_reader_keeps_text_column_keys() -> None:
    config = _config(
        reader='json',
        columns={'article': 'code_art'},
        sections=[{'columns': {'name': 'title'}}],
    )

    assert config.columns == {'article': 'code_art'}
    assert config.sections[0].columns == {'name': 'title'}


def test_behaviour_defaults() -> None:
    behavior = _config().behavior

    assert behavior.min_rest == 4
    assert behavior.rest == 'count'
    assert behavior.pipeline == DEFAULT_PIPELINE
    assert behavior.find_manufacturer_on_enrich is True
    assert behavior.collect_missing_recommended is False


def test_top_level_slots_parsed() -> None:
    config = _config(
        pricing={'policy': 'absolute', 'rules': {'markup_rules': {'k': {'min': 0, 'markup': 10}}}},
        behavior={'min_rest': 2, 'rest': 'on_request', 'pipeline': ['title']},
        category={'strategy': 'fixed', 'value': 'Шины'},
        title={'strategy': 'title_keywords'},
    )

    assert config.pricing.policy == 'absolute'
    assert isinstance(config.pricing.rules, MarkupRulesConfig)
    assert config.behavior.min_rest == 2
    assert config.behavior.rest == 'on_request'
    assert config.behavior.pipeline == ('title',)
    assert config.category.fixed_value == 'Шины'
    assert config.title.strategy == 'title_keywords'


def test_section_slots_and_overrides_parsed() -> None:
    config = _config(
        sections=[
            {
                'id': 'mim_2',
                'name': 'Мим 2',
                'start_row': 5,
                'file_templates': ['a.xls'],
                'columns': {'0': 'code'},
                'sheet_info': 'диск',
                'sheet_indexes': [0, 1],
                'category': {'strategy': 'field', 'field': 'type'},
                'title': {'strategy': 'title_keywords', 'variant': 'v1', 'aliases': True},
                'pricing': {'policy': 'percent_by_threshold', 'rules': {'threshold': 100, 'low': 5, 'high': 10}},
            }
        ]
    )
    section = config.sections[0]

    assert section.id == 'mim_2'
    assert section.name == 'Мим 2'
    assert section.start_row == 5
    assert section.file_templates == ('a.xls',)
    assert section.columns == {0: 'code'}
    assert section.sheet_info == 'диск'
    assert section.sheet_indexes == (0, 1)
    assert section.category.field_name == 'type'
    assert section.title.variant == 'v1'
    assert section.title.aliases is True
    assert section.pricing.threshold == 100
    assert section.pricing.low == 5
    assert section.pricing.high == 10


def test_section_inherits_vendor_slots() -> None:
    config = _config(
        pricing={'policy': 'absolute'},
        category={'strategy': 'fixed', 'value': 'Диск'},
        title={'strategy': 'title_keywords'},
    )
    section = config.sections[0]

    assert section.pricing.policy == 'absolute'
    assert section.category.fixed_value == 'Диск'
    assert section.title.strategy == 'title_keywords'


def test_root_must_be_object() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается объект'):
        VendorConfig.from_dict([], FOLDER, WHERE)


def test_required_key_missing_rejected() -> None:
    raw = {key: name for key, name in MINIMAL.items() if key != 'code'}

    with pytest.raises(ConfigValidationError, match='отсутствует обязательный ключ'):
        VendorConfig.from_dict(raw, FOLDER, WHERE)


def test_invalid_reader_rejected() -> None:
    with pytest.raises(ConfigValidationError, match='«reader»'):
        _config(reader='csv')


def test_sections_must_be_non_empty_list() -> None:
    with pytest.raises(ConfigValidationError, match='«sections»'):
        _config(sections=[])
    with pytest.raises(ConfigValidationError, match='«sections»'):
        _config(sections='нет')


def test_section_requires_columns() -> None:
    with pytest.raises(ConfigValidationError, match='не заданы «columns»'):
        _config(sections=[{}])


def test_section_rejects_empty_templates_override() -> None:
    with pytest.raises(ConfigValidationError, match='не задан «file_templates»'):
        _config(sections=[{'file_templates': [], 'columns': {'0': 'code'}}])


def test_xls_column_key_must_be_integer() -> None:
    with pytest.raises(ConfigValidationError, match='должен быть целым'):
        _config(sections=[{'columns': {'brand': 'manufacturer_name'}}])


def test_unknown_column_field_rejected() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестное поле «manufacturer»'):
        _config(sections=[{'columns': {'0': 'manufacturer'}}])


def test_unknown_column_field_rejected_for_json_reader() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестное поле «manufacturer»'):
        _config(reader='json', columns={'brand': 'manufacturer'})


def test_known_column_field_accepted() -> None:
    config = _config(reader='json', columns={'brand': 'manufacturer_name'})

    assert config.columns == {'brand': 'manufacturer_name'}


def test_slot_must_be_object() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается объект'):
        _config(category=[])


def test_enabled_accepts_zero_and_one() -> None:
    assert _config(enabled=0).enabled is False
    assert _config(enabled=1).enabled is True


# --------------------------------- Полное равенство: каждый ключ на месте


def test_behavior_reads_all_fields() -> None:
    """Все ключи behavior читаются в объект без потерь и подмен."""
    raw = {
        'min_rest': 9,
        'rest': 'on_request',
        'skip_markup_without_opt': True,
        'zero_rest_without_category': True,
        'collect_missing_recommended': True,
        'find_manufacturer_on_enrich': False,
        'pipeline': ['title', 'markup'],
    }

    assert BehaviorConfig.from_dict(raw, WHERE) == BehaviorConfig(
        min_rest=9,
        rest='on_request',
        skip_markup_without_opt=True,
        zero_rest_without_category=True,
        collect_missing_recommended=True,
        find_manufacturer_on_enrich=False,
        pipeline=('title', 'markup'),
    )


def test_category_reads_all_fields() -> None:
    """Все ключи category читаются в объект без потерь и подмен."""
    raw = {
        'strategy': 'field',
        'value': 'Шины',
        'field': 'type',
        'map': {'a': 'b'},
        'default': 'нет',
        'unknown_skip': True,
        'zero_rest_categories': ['x', 'y'],
    }

    assert CategoryConfig.from_dict(raw, WHERE) == CategoryConfig(
        strategy='field',
        fixed_value='Шины',
        field_name='type',
        mapping={'a': 'b'},
        default_value='нет',
        unknown_skip=True,
        zero_rest_categories=('x', 'y'),
    )


def test_title_reads_all_fields() -> None:
    """Все ключи title читаются в объект без потерь и подмен."""
    raw = {'strategy': 'title_keywords', 'variant': 'v1', 'aliases': True}

    assert TitleConfig.from_dict(raw, WHERE) == TitleConfig(
        strategy='title_keywords',
        variant='v1',
        aliases=True,
    )


def test_pricing_reads_all_fields() -> None:
    """Политика, правила и пороговые числа pricing доходят до объекта целиком."""
    raw = {
        'policy': 'percent_by_threshold',
        'rules': {
            'markup_rules': {'r': {'min': 1, 'max': 2, 'percent_markup': 3}},
            'min_recommended_percent_markup': 0.1,
            'max_recommended_percent_markup': 0.4,
            'absolute_markup_rules': {
                'min_absolute_markup': 5,
                'markup_percent': 1.5,
                'mode': ABSOLUTE_MODE_DELTA,
            },
            'replace_small_recommended': True,
            'threshold': 100,
            'low': 5,
            'high': 15,
        },
    }

    assert PricingConfig.from_dict(raw, WHERE) == PricingConfig(
        policy='percent_by_threshold',
        rules=MarkupRulesConfig(
            markup_rules={'r': MarkUpRule(min=1, max=2, percent_markup=3)},
            min_recommended_percent_markup=0.1,
            max_recommended_percent_markup=0.4,
            absolute_markup_rules=AbsoluteMarkUpRules(
                min_absolute_markup=5,
                markup_percent=1.5,
                mode=ABSOLUTE_MODE_DELTA,
            ),
            replace_small_recommended=True,
        ),
        threshold=100,
        low=5,
        high=15,
    )


def test_empty_slots_parse_to_defaults() -> None:
    """Пустой слот равен слоту по умолчанию: дефолты не подменяются мутантами."""
    assert CategoryConfig.from_dict({}, WHERE) == CategoryConfig()
    assert TitleConfig.from_dict({}, WHERE) == TitleConfig()
    assert PricingConfig.from_dict({}, WHERE) == PricingConfig()
    assert BehaviorConfig.from_dict({}, WHERE) == BehaviorConfig()


def test_section_without_keys_equals_inherited_defaults() -> None:
    """Секция только с колонками наследует весь остальной набор поставщика."""
    section = _config().sections[0]

    assert section == VendorSection(
        id='mim',
        name='Мим',
        start_row=2,
        file_templates=('*.xls',),
        columns={1: 'manufacturer_name'},
    )


def test_vendor_config_reads_all_fields() -> None:
    """Конфиг целиком, включая слоты и секции, равен ожидаемому объекту."""
    config = _config(
        columns={'2': 'title'},
        pricing={'policy': 'absolute'},
        behavior={'min_rest': 9, 'rest': 'on_request'},
        category={'strategy': 'field', 'field': 'type'},
        title={'strategy': 'title_keywords', 'variant': 'v1', 'aliases': True},
        sections=[
            {
                'id': 'sec',
                'name': 'Лист',
                'start_row': 5,
                'file_templates': ['a.xls'],
                'columns': {'0': 'code'},
                'sheet_info': 'лист',
                'sheet_indexes': [0, 1],
                'category': {'strategy': 'fixed', 'value': 'Диск'},
                'title': {'strategy': 'default', 'aliases': True},
                'pricing': {'policy': 'base', 'rules': {'threshold': 10}},
            }
        ],
    )

    assert config == VendorConfig(
        folder=FOLDER,
        enabled=True,
        code='mim',
        name='Мим',
        start_row=2,
        file_templates=('*.xls',),
        reader='xls',
        columns={2: 'title'},
        pricing=PricingConfig(policy='absolute'),
        behavior=BehaviorConfig(min_rest=9, rest='on_request'),
        category=CategoryConfig(strategy='field', field_name='type'),
        title=TitleConfig(strategy='title_keywords', variant='v1', aliases=True),
        sections=(
            VendorSection(
                id='sec',
                name='Лист',
                start_row=5,
                file_templates=('a.xls',),
                columns={0: 'code'},
                sheet_info='лист',
                sheet_indexes=(0, 1),
                category=CategoryConfig(strategy='fixed', fixed_value='Диск'),
                title=TitleConfig(aliases=True),
                pricing=PricingConfig(threshold=10),
            ),
        ),
    )
