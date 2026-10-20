"""Одно название на группу дублей: эталон, признаки шины со всей группы, моделей нет."""

from typing import Any

from domain.row_item.row_item import RowItem
from parsers.common_price_group_title import unify_group_title
from parsers.common_price_grouper import CommonPriceGrouper

_PRIORITY = {'Форточки': 1, 'Запаска': 3, 'Мим': 4}
_ALIASES: dict[str, Any] = {'Cordiant': []}


def _tire(supplier: str, title: str, model: str, **fields: Any) -> RowItem:
    payload: dict[str, Any] = {
        'supplier_name': supplier,
        'title': title,
        'model': model,
        'manufacturer_name': 'Cordiant',
        'width': '205',
        'height_percent': '65',
        'diameter': '15',
        'index_load': '94',
        'index_velocity': 'H',
        'type_production': 'Легковая шина',
        'price_markup': 10,
    }
    payload.update(fields)
    return RowItem(payload)


def _titles(group: list[RowItem]) -> set[str | None]:
    return {row_item.identity.title for row_item in group}


def test_reference_is_the_item_with_the_fullest_model() -> None:
    """Название берётся у позиции с самой полной моделью, даже если её поставщик ниже в очереди."""
    short = _tire('Форточки', '205/65R15 Cordiant Road Runner 94H', 'Road Runner')
    full = _tire('Мим', '205/65R15 Cordiant ROAD RUNNER PS-1 94H', 'ROAD RUNNER PS-1')

    unify_group_title([short, full], _PRIORITY)

    assert _titles([short, full]) == {'205/65R15 Cordiant ROAD RUNNER PS-1 94H'}


def test_priority_decides_between_equally_full_models() -> None:
    """Модели одной полноты (`ROAD RUNNER` / `Road Runner`): написание — у поставщика с меньшим местом в очереди."""
    mim = _tire('Мим', '205/65R15 Cordiant ROAD RUNNER 94H', 'ROAD RUNNER')
    zapaska = _tire('Запаска', '205/65R15 Cordiant Road Runner 94H', 'Road Runner')

    unify_group_title([mim, zapaska], _PRIORITY)

    assert _titles([mim, zapaska]) == {'205/65R15 Cordiant Road Runner 94H'}


def test_supplier_without_priority_goes_last() -> None:
    """Поставщик вне очереди эталоном не становится, пока есть поставщик с местом."""
    unknown = _tire('Новый', '205/65R15 Cordiant ROAD RUNNER 94H', 'ROAD RUNNER')
    mim = _tire('Мим', '205/65R15 Cordiant Road Runner 94H', 'Road Runner')

    unify_group_title([unknown, mim], _PRIORITY)

    assert _titles([unknown, mim]) == {'205/65R15 Cordiant Road Runner 94H'}


def test_tire_features_of_any_item_reach_every_title_in_canonical_order() -> None:
    """`XL`, `TL`, `M+S`, `3PMSF` и ось, найденные хотя бы у одной позиции, пишутся в общее название по порядку."""
    plain = _tire('Форточки', '205/65R15 Cordiant Road Runner 94H', 'Road Runner')
    featured = _tire('Запаска', '205/65R15 Cordiant Road Runner 94H XL TL M+S 3PMSF Рулевая', 'Road Runner')

    unify_group_title([plain, featured], _PRIORITY)

    expected = '205/65R15 Cordiant Road Runner 94H XL TL M+S 3PMSF Рулевая'
    assert _titles([plain, featured]) == {expected}


def test_reference_layering_and_unknown_tokens_are_kept() -> None:
    """Слойность и незнакомые слова хвоста остаются на своих местах: слова до `XL`, `<N>PR` после."""
    reference = _tire('Форточки', '205/65R15 Cordiant Road Runner 94H Extra 8PR TT RunFlat', 'Road Runner')
    other = _tire('Мим', '205/65R15 Cordiant Road Runner 94H XL', 'Road Runner')

    unify_group_title([reference, other], _PRIORITY)

    assert _titles([reference, other]) == {'205/65R15 Cordiant Road Runner 94H Extra XL 8PR TT RunFlat'}


def test_title_without_load_index_is_taken_as_is() -> None:
    """Нет нагрузки+скорости в названии эталона — признаки не добавляются, берётся название эталона."""
    reference = _tire('Форточки', '205/65R15 Cordiant Road Runner', 'Road Runner', index_load='', index_velocity='')
    other = _tire('Мим', '205/65R15 Cordiant Road Runner 94H XL', 'Road Runner')

    unify_group_title([reference, other], _PRIORITY)

    assert _titles([reference, other]) == {'205/65R15 Cordiant Road Runner'}


def test_items_without_models_take_the_fullest_title() -> None:
    """Камеры без модели: название полнее у той, где указана модель камеры (`ГК-230`)."""
    short = RowItem({'supplier_name': 'Пионер', 'title': 'Камера 17.5-25', 'type_production': 'Автокамера'})
    full = RowItem({'supplier_name': 'Пошк', 'title': 'Камера 17.5-25 ГК-230', 'type_production': 'Автокамера'})

    unify_group_title([short, full], {})

    assert _titles([short, full]) == {'Камера 17.5-25 ГК-230'}


def test_same_titles_are_left_alone() -> None:
    """Одинаковые названия не трогаются."""
    first = _tire('Форточки', '205/65R15 Cordiant Road Runner 94H', 'Road Runner')
    second = _tire('Мим', '205/65R15 Cordiant Road Runner 94H', 'Road Runner')

    unify_group_title([first, second], _PRIORITY)

    assert _titles([first, second]) == {'205/65R15 Cordiant Road Runner 94H'}


def test_grouper_unifies_titles_of_one_group_only() -> None:
    """Группировщик сводит названия внутри группы и не смешивает разные группы."""
    left = _tire('Форточки', '205/65R15 Cordiant Road Runner 94H', 'Road Runner')
    right = _tire('Мим', '205/65R15 Cordiant Road Runner 94H XL', 'Road Runner')
    foreign = _tire('Мим', '215/65R16 Cordiant Road Runner 98H', 'Road Runner', width='215', diameter='16')

    CommonPriceGrouper([left, right, foreign], _ALIASES, _PRIORITY).group_by_params()

    assert left.identity.title == right.identity.title == '205/65R15 Cordiant Road Runner 94H XL'
    assert foreign.identity.title == '215/65R16 Cordiant Road Runner 98H'
