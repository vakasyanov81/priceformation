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

GROUP_PATH = f'{WHERE} → product_groups[0]'


def _raw(**group: Any) -> dict[str, Any]:
    """Валидный поставщик с переопределениями своей группы и явными ID секций."""
    return {
        'code': 'mim',
        'name': 'Мим',
        'product_groups': [
            {
                'id': 'tire_and_disk',
                'start_row': 2,
                'file_templates': ['*.xls'],
                'columns': {'2': 'title'},
                'sections': [{'id': 'mim', 'columns': {'1': 'manufacturer_name'}}],
                **group,
            }
        ],
    }


def _json_columns_raw() -> dict[str, Any]:
    group = {**_raw()['product_groups'][0], 'columns': [42]}
    return {**_raw(), 'reader': 'json', 'product_groups': [group]}


# (конфиг, фрагмент пути, который обязан быть в сообщении)
PATH_CASES = [
    # корень и ключи верхнего уровня
    ({**_raw(), 'reader': 5}, f'{WHERE} → reader'),
    ({**_raw(), 'code': 5}, f'{WHERE} → code'),
    ({**_raw(), 'source': 5}, f'{WHERE} → source'),
    ({**_raw(), 'name': 5}, f'{WHERE} → name'),
    (_raw(start_row='x'), f'{GROUP_PATH} → start_row'),
    (_raw(file_templates='x'), f'{GROUP_PATH} → file_templates'),
    (_raw(id='unknown'), f'{GROUP_PATH}.id'),
    (_raw(sections=[{'id': 'mim', 'row_selector': []}]), f'{GROUP_PATH} → sections[0] → row_selector'),
    (
        _raw(sections=[{'id': 'mim', 'row_selector': {'column': 42, 'values': ['x']}}]),
        f'{GROUP_PATH} → sections[0] → row_selector → column',
    ),
    (_raw(section_selector=[]), f'{GROUP_PATH} → section_selector'),
    (_json_columns_raw(), GROUP_PATH),
    (_raw(columns='x'), GROUP_PATH),
    (_raw(columns={'brand': 'title'}), f'{GROUP_PATH} → brand'),
    (_raw(columns={'9': 'nope'}), f'{GROUP_PATH} → columns[9]'),
    # pricing
    (_raw(pricing='x'), f'{GROUP_PATH} → pricing'),
    (_raw(pricing={'policy': 5}), f'{GROUP_PATH} → pricing → policy'),
    (_raw(pricing={'rules': 'x'}), f'{GROUP_PATH} → pricing → rules'),
    (
        _raw(pricing={'rules': {'threshold': 'x'}}),
        f'{GROUP_PATH} → pricing → rules',
    ),
    (_raw(pricing={'rules': {'low': 'x'}}), f'{GROUP_PATH} → pricing → rules'),
    (_raw(pricing={'rules': {'high': 'x'}}), f'{GROUP_PATH} → pricing → rules'),
    (
        _raw(pricing={'rules': {'min_recommended_percent_markup': 'x'}}),
        f'{GROUP_PATH} → pricing → rules',
    ),
    (
        _raw(pricing={'rules': {'max_recommended_percent_markup': 'x'}}),
        f'{GROUP_PATH} → pricing → rules',
    ),
    (
        _raw(pricing={'rules': {'replace_small_recommended': 1}}),
        f'{GROUP_PATH} → pricing → rules',
    ),
    (
        _raw(pricing={'rules': {'markup_rules': 'x'}}),
        f'{GROUP_PATH} → pricing → rules → markup_rules',
    ),
    (
        _raw(pricing={'rules': {'markup_rules': {'r': 'x'}}}),
        f'{GROUP_PATH} → pricing → rules → markup_rules',
    ),
    (
        _raw(pricing={'rules': {'markup_rules': {'r': {'max': 'x'}}}}),
        f'{GROUP_PATH} → pricing → rules → markup_rules.r',
    ),
    (
        _raw(pricing={'rules': {'absolute_markup_rules': 'x'}}),
        f'{GROUP_PATH} → pricing → rules → absolute_markup_rules',
    ),
    (
        _raw(pricing={'rules': {'absolute_markup_rules': {'min_absolute_markup': 'x'}}}),
        f'{GROUP_PATH} → pricing → rules → absolute_markup_rules',
    ),
    (
        _raw(pricing={'rules': {'absolute_markup_rules': {'markup_percent': 'x'}}}),
        f'{GROUP_PATH} → pricing → rules → absolute_markup_rules',
    ),
    (
        _raw(pricing={'rules': {'absolute_markup_rules': {'mode': 'bad'}}}),
        f'{GROUP_PATH} → pricing → rules → absolute_markup_rules',
    ),
    # behavior
    (_raw(behavior='x'), f'{GROUP_PATH} → behavior'),
    (_raw(behavior={'min_rest': 'x'}), f'{GROUP_PATH} → behavior → min_rest'),
    (_raw(behavior={'rest': 5}), f'{GROUP_PATH} → behavior → rest'),
    (_raw(behavior={'pipeline': 'x'}), f'{GROUP_PATH} → behavior → pipeline'),
    (_raw(behavior={'warehouse_cities': 42}), f'{GROUP_PATH} → behavior → warehouse_cities'),
    (_raw(behavior={'manufacturer_column_first': 'x'}), f'{GROUP_PATH} → behavior'),
    (_raw(behavior={'order_from_warehouse_name': 'x'}), f'{GROUP_PATH} → behavior'),
    (_raw(behavior={'api_types': 'x'}), f'{GROUP_PATH} → behavior'),
    *[
        (_raw(behavior={key: 'x'}), f'{GROUP_PATH} → behavior: «{key}»')
        for key in (
            'skip_markup_without_opt',
            'zero_rest_without_category',
            'collect_missing_recommended',
            'find_manufacturer_on_enrich',
        )
    ],
    # category
    (_raw(category='x'), f'{GROUP_PATH} → category'),
    (_raw(category={'strategy': 5}), f'{GROUP_PATH} → category → strategy'),
    (_raw(category={'value': 5}), f'{GROUP_PATH} → category → value'),
    (_raw(category={'field': 5}), f'{GROUP_PATH} → category → field'),
    (_raw(category={'map': 'x'}), f'{GROUP_PATH} → category: «map»'),
    (_raw(category={'default': 5}), f'{GROUP_PATH} → category → default'),
    (_raw(category={'unknown_skip': 'x'}), f'{GROUP_PATH} → category: «unknown_skip»'),
    (
        _raw(category={'zero_rest_categories': 'x'}),
        f'{GROUP_PATH} → category → zero_rest_categories',
    ),
    # size_fields категории: путь доходит до категории и поля
    (_raw(category={'size_fields': 'x'}), f'{GROUP_PATH} → category → size_fields'),
    (
        _raw(category={'size_fields': {'Грузовая шина': 'x'}}),
        f'{GROUP_PATH} → category → size_fields → Грузовая шина',
    ),
    (
        _raw(category={'size_fields': {'': {'season': 'Всесезонная'}}}),
        f'{GROUP_PATH} → category → size_fields',
    ),
    (
        _raw(category={'size_fields': {'Спецшина': {'nope': 'x'}}}),
        f'{GROUP_PATH} → category → size_fields → Спецшина',
    ),
    (
        _raw(category={'size_fields': {'Спецшина': {'season': 5}}}),
        f'{GROUP_PATH} → category → size_fields → Спецшина → season',
    ),
    (_raw(category={'calculate_type': 'x'}), f'{GROUP_PATH} → category'),
    (_raw(category={'light_truck_by_diameter': 'x'}), f'{GROUP_PATH} → category'),
    # title
    (_raw(title='x'), f'{GROUP_PATH} → title'),
    (_raw(title={'strategy': 5}), f'{GROUP_PATH} → title → strategy'),
    (_raw(title={'variant': 5}), f'{GROUP_PATH} → title → variant'),
    (_raw(title={'aliases': 'x'}), f'{GROUP_PATH} → title: «aliases»'),
    (_raw(title={'fallback_brand': 5}), f'{GROUP_PATH} → title → fallback_brand'),
    (_raw(title={'camera_by_kind': 'x'}), f'{GROUP_PATH} → title'),
    # маркеры title: путь доходит до маркера и поля
    (_raw(title={'markers': 'x'}), f'{GROUP_PATH} → title → markers'),
    (_raw(title={'markers': {'шип': 'x'}}), f'{GROUP_PATH} → title → markers → шип'),
    (_raw(title={'markers': {'': {'season': 'зима'}}}), f'{GROUP_PATH} → title → markers'),
    (
        _raw(title={'markers': {'шип': {'nope': 'x'}}}),
        f'{GROUP_PATH} → title → markers → шип',
    ),
    (
        _raw(title={'markers': {'шип': {'season': 5}}}),
        f'{GROUP_PATH} → title → markers → шип → season',
    ),
    # секции: путь обязан доходить до sections[i]
    (_raw(sections=[[]]), f'{GROUP_PATH} → sections[0]'),
    (_raw(sections=[{'id': 5}]), f'{GROUP_PATH} → sections[0].id'),
    (_raw(sections=[{'id': 'mim', 'name': 5}]), f'{GROUP_PATH} → sections[0] → name'),
    (_raw(sections=[{'id': 'mim', 'start_row': 'x'}]), f'{GROUP_PATH} → sections[0] → start_row'),
    (_raw(sections=[{'id': 'mim', 'file_templates': 'x'}]), f'{GROUP_PATH} → sections[0] → file_templates'),
    (_raw(sections=[{'id': 'mim', 'columns': 'x'}]), f'{GROUP_PATH} → sections[0]'),
    (_raw(sections=[{'id': 'mim', 'columns': {'0': 'nope'}}]), f'{GROUP_PATH} → sections[0] → columns[0]'),
    (_raw(sections=[{'id': 'mim', 'columns': {'brand': 'title'}}]), f'{GROUP_PATH} → sections[0] → brand'),
    (_raw(sections=[{'id': 'mim', 'sheet_info': 5}]), f'{GROUP_PATH} → sections[0] → sheet_info'),
    (_raw(sections=[{'id': 'mim', 'sheet_indexes': 'x'}]), f'{GROUP_PATH} → sections[0]'),
    (_raw(sections=[{'id': 'mim', 'sheet_indexes': [1.5]}]), f'{GROUP_PATH} → sections[0] → sheet_indexes'),
    # слоты внутри секции: путь не должен обрываться на sections[i]
    (_raw(sections=[{'id': 'mim', 'category': 'x'}]), f'{GROUP_PATH} → sections[0] → category'),
    (
        _raw(sections=[{'id': 'mim', 'category': {'unknown_skip': 'x'}}]),
        f'{GROUP_PATH} → sections[0] → category: «unknown_skip»',
    ),
    (_raw(sections=[{'id': 'mim', 'title': 'x'}]), f'{GROUP_PATH} → sections[0] → title'),
    (
        _raw(sections=[{'id': 'mim', 'title': {'aliases': 'x'}}]),
        f'{GROUP_PATH} → sections[0] → title: «aliases»',
    ),
    (_raw(sections=[{'id': 'mim', 'pricing': 'x'}]), f'{GROUP_PATH} → sections[0] → pricing'),
    (
        _raw(sections=[{'id': 'mim', 'pricing': {'policy': 5}}]),
        f'{GROUP_PATH} → sections[0] → pricing → policy',
    ),
    (
        _raw(sections=[{'id': 'mim', 'pricing': {'rules': {'threshold': 'x'}}}]),
        f'{GROUP_PATH} → sections[0] → pricing → rules',
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
