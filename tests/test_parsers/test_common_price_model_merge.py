"""tests for model merge by token sets."""

import pytest

from domain.row_item.row_item import RowItem
from parsers.common_price.group_key import MODEL_KEY_INDEX
from parsers.common_price.model import clear_model, model_tokens
from parsers.common_price.model_keys import keys_with_merged_models
from parsers.common_price.model_merge import ModelEntry, merge_models


def _entry(model: str) -> ModelEntry:
    return model.replace(' ', ''), frozenset(model.split())


def _entries(*models: str) -> list[ModelEntry]:
    return [_entry(model) for model in models]


def test_short_model_joins_the_only_longer_one() -> None:
    merged = merge_models(_entries('g075', 'ice guard g075'))
    assert merged['g075'] == merged['iceguardg075'] == 'iceguardg075'


def test_short_model_joins_nearest_longer_one_through_the_chain() -> None:
    """`gravity` входит и в `gravity suv`, и в `gravity suv ps9`: берём ближайшую и идём дальше по цепочке."""
    merged = merge_models(_entries('gravity', 'gravity suv', 'gravity suv ps9'))
    assert merged['gravity'] == merged['gravitysuv'] == merged['gravitysuvps9'] == 'gravitysuvps9'


def test_separately_written_words_are_inside_joined_ones() -> None:
    """`ice guard g075` входит в `iceguard studless g075`, поэтому `g075` идёт к ближайшей и дальше по цепочке."""
    merged = merge_models(_entries('g075', 'ice guard g075', 'iceguard studless g075'))
    assert merged['g075'] == merged['iceguardg075'] == merged['iceguardstudlessg075'] == 'iceguardstudlessg075'


def test_equally_near_unrelated_longer_models_leave_short_one_alone() -> None:
    """`g075` входит в две длинные одного размера, не связанные друг с другом: не склеиваем."""
    merged = merge_models(_entries('g075', 'ice guard g075', 'blue earth g075'))
    assert merged['g075'] == 'g075'
    assert merged['iceguardg075'] == 'iceguardg075'


def test_same_words_different_order_merge() -> None:
    merged = merge_models(_entries('hk241 grant', 'grant hk241'))
    assert merged['hk241grant'] == merged['granthk241'] == 'granthk241'


def test_unrelated_models_stay_apart() -> None:
    merged = merge_models(_entries('gravity', 'winter drive'))
    assert merged == {'gravity': 'gravity', 'winterdrive': 'winterdrive'}


def test_models_without_words_are_skipped() -> None:
    entries = [('', frozenset[str]()), *_entries('x')]
    assert merge_models(entries) == {'x': 'x'}


def test_empty_model_key_is_kept_after_merging() -> None:
    rows = [
        RowItem({'type_production': 'легковая', 'width': '205', 'diameter': '16'}),
        RowItem({'type_production': 'легковая', 'width': '205', 'diameter': '16', 'model': 'Gravity'}),
    ]

    keyed = keys_with_merged_models(rows, {})

    empty_key = keyed[0][0]
    model_key = keyed[1][0]
    assert empty_key[MODEL_KEY_INDEX] == ''
    assert empty_key[:MODEL_KEY_INDEX] + empty_key[MODEL_KEY_INDEX + 1 :] == (
        model_key[:MODEL_KEY_INDEX] + model_key[MODEL_KEY_INDEX + 1 :]
    )


def test_model_key_tokens_strip_manufacturer_and_brand() -> None:
    base = {'type_production': 'легковая', 'width': '205', 'diameter': '16'}
    rows = [
        RowItem(base | {'model': 'Gravity', 'manufacturer_name': 'Cordiant'}),
        RowItem(base | {'model': 'Cordiant Gravity SUV', 'manufacturer_name': 'Cordiant'}),
        RowItem(base | {'model': 'PS-1', 'manufacturer_name': 'Cordiant', 'brand': 'Road Runner'}),
        RowItem(base | {'model': 'Road Runner PS-1 Extra', 'manufacturer_name': 'Cordiant', 'brand': 'Road Runner'}),
    ]

    keyed = keys_with_merged_models(rows, {})

    assert keyed[0][0] == keyed[1][0]
    assert keyed[2][0] == keyed[3][0]


def test_transliterated_cyrillic_model_joins_longer_latin_one() -> None:
    """`Бел-298` и `Escortera DN500 BEL-298` — одна шина: короткая модель входит в длинную."""
    long_model, short_model = 'Escortera DN500 BEL-298', 'Бел-298'
    entries = [(clear_model(model), model_tokens(model)) for model in (long_model, short_model)]
    merged = merge_models(entries)
    long_key = clear_model(long_model)
    assert merged[clear_model(short_model)] == merged[long_key] == long_key


def test_word_prefix_does_not_merge_unrelated_models() -> None:
    """Совпавшего префикса недостаточно: обе раздельные части должны входить в короткую модель."""
    assert merge_models(_entries('ice', 'icewinter')) == {'ice': 'ice', 'icewinter': 'icewinter'}


def test_entries_with_only_key_or_only_tokens_are_skipped() -> None:
    """Пустые слова и пустой ключ независимо исключают запись из карты моделей."""
    no_words: ModelEntry = ('empty', frozenset())
    no_key: ModelEntry = ('', frozenset(('ice',)))
    entries = [no_words, no_key, *_entries('winter')]
    assert merge_models(entries) == {'winter': 'winter'}


def test_models_from_different_manufacturers_stay_apart() -> None:
    """Надмножество слов чужого производителя не меняет модель своей группы."""
    rows = [
        RowItem({'model': 'Gravity', 'manufacturer_name': 'Cordiant'}),
        RowItem({'model': 'Gravity SUV', 'manufacturer_name': 'Ikon'}),
    ]

    keyed = keys_with_merged_models(rows, {})

    assert [key[MODEL_KEY_INDEX] for key, _row in keyed] == ['gravity', 'gravitysuv']
    assert [row for _key, row in keyed] == rows


@pytest.mark.parametrize('prefix_field', ['manufacturer_name', 'brand'])
def test_prefix_on_short_model_does_not_prevent_merging(prefix_field: str) -> None:
    """Префикс короткой модели удаляется до поиска её надмножества без префикса."""
    rows = [
        RowItem({prefix_field: 'Cordiant', 'model': 'Cordiant Gravity'}),
        RowItem({prefix_field: 'Cordiant', 'model': 'Gravity SUV'}),
    ]

    keyed = keys_with_merged_models(rows, {})

    assert keyed[0][0] == keyed[1][0]
    assert keyed[0][0][MODEL_KEY_INDEX] == 'gravitysuv'
    assert [row for _key, row in keyed] == rows


def test_hyphen_between_manufacturer_and_brand_does_not_leave_brand_tokens() -> None:
    """Удаление первого префикса открывает второй, даже если они разделены дефисом."""
    assert model_tokens('Cordiant-Road PS-1', 'Cordiant', 'Road') == frozenset(('ps1',))


@pytest.mark.parametrize(
    ('short', 'long', 'target'),
    [
        ('a ab abc ba bc', 'aba abcab bc', 'long'),
        ('a ab abc ba bc', 'aba abcab bc extra', 'long'),
        ('a ab abc bc', 'aba abcab bc', 'short'),
        ('ice', 'iceice', 'short'),
    ],
)
def test_joined_words_require_consistent_pairs(short: str, long: str, target: str) -> None:
    """Все раздельные слова покрываются непересекающимися парами, лишние слитные допустимы."""
    short_entry = ('short', frozenset(short.split()))
    long_entry = ('long', frozenset(long.split()))
    entries = [short_entry, long_entry]
    expected = {'short': target, 'long': 'long'}
    assert merge_models(entries) == expected
    assert merge_models(reversed(entries)) == expected
