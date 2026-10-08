"""Сообщения об ошибках конфига поставщика содержат полный путь до ключа.

Мутанты `where → None` и `f'{where} → …' → None` выживают, когда тест матчит
только устойчивую часть сообщения («ожидается объект», «должно быть числом»).
Здесь ассерт — это путь: по нему пользователь правит свой JSON.
"""

from collections.abc import Callable
from typing import Any

import pytest

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.slot_configs import BehaviorConfig, CategoryConfig, PricingConfig, TitleConfig

FOLDER = 'mim'
WHERE = 'mim.json'

MINIMAL: dict[str, Any] = {
    'enabled': 1,
    'code': 'mim',
    'name': 'Мим',
    'start_row': 2,
    'file_templates': ['*.xls'],
    'columns': {'2': 'title'},
    'sections': [{'columns': {'1': 'manufacturer_name'}}],
}


def _raw(**overrides: Any) -> dict[str, Any]:
    """Минимальный валидный конфиг с перекрытыми ключами."""
    return {**MINIMAL, **overrides}


# (конфиг, фрагмент пути, который обязан быть в сообщении)
PATH_CASES = [
    # корень и ключи верхнего уровня
    ({**_raw(), 'reader': 5}, f'{WHERE} → reader'),
    ({**_raw(), 'enabled': 5}, WHERE),
    ({**_raw(), 'name': 5}, f'{WHERE} → name'),
    ({**_raw(), 'start_row': 'x'}, f'{WHERE} → start_row'),
    ({**_raw(), 'file_templates': 'x'}, f'{WHERE} → file_templates'),
    ({**_raw(), 'columns': 'x'}, WHERE),
    ({**_raw(), 'columns': {'brand': 'title'}}, f'{WHERE} → brand'),
    ({**_raw(), 'columns': {'9': 'nope'}}, f'{WHERE} → columns[9]'),
    # pricing
    ({**_raw(), 'pricing': 'x'}, f'{WHERE} → pricing'),
    ({**_raw(), 'pricing': {'policy': 5}}, f'{WHERE} → pricing → policy'),
    ({**_raw(), 'pricing': {'rules': 'x'}}, f'{WHERE} → pricing → rules'),
    (
        {**_raw(), 'pricing': {'rules': {'threshold': 'x'}}},
        f'{WHERE} → pricing → rules',
    ),
    ({**_raw(), 'pricing': {'rules': {'low': 'x'}}}, f'{WHERE} → pricing → rules'),
    ({**_raw(), 'pricing': {'rules': {'high': 'x'}}}, f'{WHERE} → pricing → rules'),
    (
        {**_raw(), 'pricing': {'rules': {'min_recommended_percent_markup': 'x'}}},
        f'{WHERE} → pricing → rules',
    ),
    (
        {**_raw(), 'pricing': {'rules': {'max_recommended_percent_markup': 'x'}}},
        f'{WHERE} → pricing → rules',
    ),
    (
        {**_raw(), 'pricing': {'rules': {'replace_small_recommended': 1}}},
        f'{WHERE} → pricing → rules',
    ),
    (
        {**_raw(), 'pricing': {'rules': {'markup_rules': 'x'}}},
        f'{WHERE} → pricing → rules → markup_rules',
    ),
    (
        {**_raw(), 'pricing': {'rules': {'markup_rules': {'r': 'x'}}}},
        f'{WHERE} → pricing → rules → markup_rules',
    ),
    (
        {**_raw(), 'pricing': {'rules': {'markup_rules': {'r': {'max': 'x'}}}}},
        f'{WHERE} → pricing → rules → markup_rules.r',
    ),
    (
        {**_raw(), 'pricing': {'rules': {'absolute_markup_rules': 'x'}}},
        f'{WHERE} → pricing → rules → absolute_markup_rules',
    ),
    (
        {**_raw(), 'pricing': {'rules': {'absolute_markup_rules': {'min_absolute_markup': 'x'}}}},
        f'{WHERE} → pricing → rules → absolute_markup_rules',
    ),
    (
        {**_raw(), 'pricing': {'rules': {'absolute_markup_rules': {'markup_percent': 'x'}}}},
        f'{WHERE} → pricing → rules → absolute_markup_rules',
    ),
    (
        {**_raw(), 'pricing': {'rules': {'absolute_markup_rules': {'mode': 'bad'}}}},
        f'{WHERE} → pricing → rules → absolute_markup_rules',
    ),
    # behavior
    ({**_raw(), 'behavior': 'x'}, f'{WHERE} → behavior'),
    ({**_raw(), 'behavior': {'min_rest': 'x'}}, f'{WHERE} → behavior → min_rest'),
    ({**_raw(), 'behavior': {'rest': 5}}, f'{WHERE} → behavior → rest'),
    ({**_raw(), 'behavior': {'pipeline': 'x'}}, f'{WHERE} → behavior → pipeline'),
    *[
        ({**_raw(), 'behavior': {key: 'x'}}, f'{WHERE} → behavior: «{key}»')
        for key in (
            'skip_markup_without_opt',
            'zero_rest_without_category',
            'collect_missing_recommended',
            'find_manufacturer_on_enrich',
        )
    ],
    # category
    ({**_raw(), 'category': 'x'}, f'{WHERE} → category'),
    ({**_raw(), 'category': {'strategy': 5}}, f'{WHERE} → category → strategy'),
    ({**_raw(), 'category': {'value': 5}}, f'{WHERE} → category → value'),
    ({**_raw(), 'category': {'field': 5}}, f'{WHERE} → category → field'),
    ({**_raw(), 'category': {'map': 'x'}}, f'{WHERE} → category: «map»'),
    ({**_raw(), 'category': {'default': 5}}, f'{WHERE} → category → default'),
    ({**_raw(), 'category': {'unknown_skip': 'x'}}, f'{WHERE} → category: «unknown_skip»'),
    (
        {**_raw(), 'category': {'zero_rest_categories': 'x'}},
        f'{WHERE} → category → zero_rest_categories',
    ),
    # title
    ({**_raw(), 'title': 'x'}, f'{WHERE} → title'),
    ({**_raw(), 'title': {'strategy': 5}}, f'{WHERE} → title → strategy'),
    ({**_raw(), 'title': {'variant': 5}}, f'{WHERE} → title → variant'),
    ({**_raw(), 'title': {'aliases': 'x'}}, f'{WHERE} → title: «aliases»'),
    # секции: путь обязан доходить до sections[i]
    ({**_raw(), 'sections': [[]]}, f'{WHERE} → sections[0]'),
    ({**_raw(), 'sections': [{'id': 5}]}, f'{WHERE} → sections[0] → id'),
    ({**_raw(), 'sections': [{'name': 5}]}, f'{WHERE} → sections[0] → name'),
    ({**_raw(), 'sections': [{'start_row': 'x'}]}, f'{WHERE} → sections[0] → start_row'),
    ({**_raw(), 'sections': [{'file_templates': 'x'}]}, f'{WHERE} → sections[0] → file_templates'),
    ({**_raw(), 'sections': [{'columns': 'x'}]}, f'{WHERE} → sections[0]'),
    ({**_raw(), 'sections': [{'columns': {'0': 'nope'}}]}, f'{WHERE} → sections[0] → columns[0]'),
    ({**_raw(), 'sections': [{'columns': {'brand': 'title'}}]}, f'{WHERE} → sections[0] → brand'),
    ({**_raw(), 'sections': [{'sheet_info': 5}]}, f'{WHERE} → sections[0] → sheet_info'),
    ({**_raw(), 'sections': [{'sheet_indexes': 'x'}]}, f'{WHERE} → sections[0]'),
    ({**_raw(), 'sections': [{'sheet_indexes': [1.5]}]}, f'{WHERE} → sections[0] → sheet_indexes'),
    # слоты внутри секции: путь не должен обрываться на sections[i]
    ({**_raw(), 'sections': [{'category': 'x'}]}, f'{WHERE} → sections[0] → category'),
    (
        {**_raw(), 'sections': [{'category': {'unknown_skip': 'x'}}]},
        f'{WHERE} → sections[0] → category: «unknown_skip»',
    ),
    ({**_raw(), 'sections': [{'title': 'x'}]}, f'{WHERE} → sections[0] → title'),
    (
        {**_raw(), 'sections': [{'title': {'aliases': 'x'}}]},
        f'{WHERE} → sections[0] → title: «aliases»',
    ),
    ({**_raw(), 'sections': [{'pricing': 'x'}]}, f'{WHERE} → sections[0] → pricing'),
    (
        {**_raw(), 'sections': [{'pricing': {'policy': 5}}]},
        f'{WHERE} → sections[0] → pricing → policy',
    ),
    (
        {**_raw(), 'sections': [{'pricing': {'rules': {'threshold': 'x'}}}]},
        f'{WHERE} → sections[0] → pricing → rules',
    ),
]


@pytest.mark.parametrize(('raw', 'path'), PATH_CASES, ids=range(len(PATH_CASES)))
def test_error_message_contains_full_path(raw: dict[str, Any], path: str) -> None:
    """Путь до ключа — в каждой ошибке разбора: без него конфиг не правится."""
    with pytest.raises(ConfigValidationError) as exc_info:
        VendorConfig.from_dict(raw, FOLDER, WHERE)

    assert path in str(exc_info.value)


def test_root_must_be_object_with_path() -> None:
    """Корень конфига не объект — путь в сообщении есть."""
    with pytest.raises(ConfigValidationError) as exc_info:
        VendorConfig.from_dict([], FOLDER, WHERE)

    assert str(exc_info.value).startswith(WHERE)


SLOT_ROOT_PARSERS: list[Callable[[Any, str], Any]] = [
    BehaviorConfig.from_dict,
    CategoryConfig.from_dict,
    TitleConfig.from_dict,
    PricingConfig.from_dict,
]


@pytest.mark.parametrize('parse', SLOT_ROOT_PARSERS, ids=['behavior', 'category', 'title', 'pricing'])
def test_slot_root_must_be_object_with_path(parse: Callable[[Any, str], Any]) -> None:
    """Каждый слот напрямую тоже указывает путь, а не только «ожидается объект»."""
    with pytest.raises(ConfigValidationError) as exc_info:
        parse([], WHERE)

    assert str(exc_info.value).startswith(WHERE)
