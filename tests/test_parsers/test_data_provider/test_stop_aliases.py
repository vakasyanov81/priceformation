"""tests for manufacturer aliases providers"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from parsers.data_provider.manufacturer_aliases import (
    ManufacturerAliasesProviderBase,
    ManufacturerAliasesProviderFromUserConfig,
    aliases_for_finder,
    clear_manufacturer_aliases_cache,
    drop_blank_aliases,
    load_aliases_map,
)
from parsers.data_provider.manufacturer_group import manufacturer_group

_PROVIDER = MagicMock(config_file=MagicMock(return_value='manufacturer_aliases.json'))


def test_aliases_base_raises() -> None:
    with pytest.raises(NotImplementedError):
        ManufacturerAliasesProviderBase().get_aliases()


def test_aliases_from_config() -> None:
    with patch('parsers.data_provider.manufacturer_aliases.read_file', return_value='{"A": "B"}'):
        assert ManufacturerAliasesProviderFromUserConfig(_PROVIDER).get_aliases() == {'A': 'B'}


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ({'Brand': ['']}, {'Brand': []}),
        ({'Brand': [' ']}, {'Brand': []}),
        ({'Brand': ['', ' ', 'Bar']}, {'Brand': ['Bar']}),
        ({'Brand': []}, {'Brand': []}),
        ({'A': 'B'}, {'A': 'B'}),
        (
            {'НКШЗ': {'aliases': ['', ' ', 'НК.ШЗ'], 'group': 'кама'}},
            {'НКШЗ': {'aliases': ['НК.ШЗ'], 'group': 'кама'}},
        ),
        (
            {'Aeolus': ['Аеолус']},
            {'Aeolus': ['Аеолус']},
        ),
    ],
)
def test_drop_blank_aliases(raw: Any, expected: Any) -> None:
    assert drop_blank_aliases(raw) == expected


def test_aliases_for_finder_object_and_list() -> None:
    raw = {
        'НКШЗ': ['НК.ШЗ', 'Нк.шз', 'Кама', 'Kama'],
        'Aeolus': ['Аеолус'],
        'Cordiant': {'aliases': ['КОРДИАНТ'], 'group': 'cordiant'},
    }
    assert aliases_for_finder(raw) == {
        'НКШЗ': ('НК.ШЗ', 'Нк.шз', 'Кама', 'Kama'),
        'Aeolus': ('Аеолус',),
        'Cordiant': ('КОРДИАНТ',),
    }


def test_aliases_for_finder_string_and_invalid() -> None:
    assert aliases_for_finder({'A': 'B'}) == {'A': ('B',)}
    assert aliases_for_finder({'A': ''}) == {'A': ()}
    assert aliases_for_finder({'A': None}) == {'A': ()}


def test_drop_blank_aliases_skips_nonstring_items() -> None:
    """_filled_aliases пропускает нестроковые элементы списка."""
    cleaned = drop_blank_aliases({'Brand': ['OK', None, 123, '']})
    assert cleaned == {'Brand': ['OK']}


def test_manufacturer_group_uses_group_or_key() -> None:
    aliases = {
        'НКШЗ': ['НК.ШЗ', 'Кама', 'Kama'],
        'Aeolus': ['Аеолус'],
        'Cordiant': {'aliases': ['КОРДИАНТ'], 'group': 'cordiant'},
    }
    assert manufacturer_group('НКШЗ', aliases) == 'нкшз'
    assert manufacturer_group('Кама', aliases) == 'нкшз'
    assert manufacturer_group('Kama', aliases) == 'нкшз'
    assert manufacturer_group('Aeolus', aliases) == 'aeolus'
    assert manufacturer_group('Triangle', aliases) == 'triangle'
    assert manufacturer_group('', aliases) == ''
    assert manufacturer_group('НКШЗ', {}) == 'нкшз'
    assert manufacturer_group('Cordiant', aliases) == 'cordiant'
    assert manufacturer_group('Aeolus', {'Aeolus': {'aliases': [], 'group': ''}}) == 'aeolus'


def test_manufacturer_group_lookup_once_per_map() -> None:
    aliases = {'НКШЗ': ['Кама']}
    with patch(
        'parsers.data_provider.manufacturer_group.aliases_for_finder',
        wraps=aliases_for_finder,
    ) as finder:
        assert manufacturer_group('Кама', aliases) == 'нкшз'
        assert manufacturer_group('НКШЗ', aliases) == 'нкшз'
        assert finder.call_count == 1


def test_load_aliases_map_missing_file() -> None:
    clear_manufacturer_aliases_cache()
    with patch('parsers.data_provider.manufacturer_aliases.read_file', side_effect=FileNotFoundError):
        assert load_aliases_map(_PROVIDER) == {}
    clear_manufacturer_aliases_cache()


def test_load_aliases_map_reloads_after_clear() -> None:
    """FileNotFound кэширует {}; после сброса появляется файл."""
    clear_manufacturer_aliases_cache()
    with patch('parsers.data_provider.manufacturer_aliases.read_file', side_effect=[FileNotFoundError, '{"A": "B"}']):
        assert load_aliases_map(_PROVIDER) == {}
        assert load_aliases_map(_PROVIDER) == {}
        clear_manufacturer_aliases_cache()
        assert load_aliases_map(_PROVIDER) == {'A': 'B'}
    clear_manufacturer_aliases_cache()


def test_aliases_from_config_drops_blanks() -> None:
    with patch('parsers.data_provider.manufacturer_aliases.read_file', return_value='{"Brand": ["", " ", "Bar"]}'):
        assert ManufacturerAliasesProviderFromUserConfig(_PROVIDER).get_aliases() == {'Brand': ['Bar']}


def test_filled_aliases_keeps_values_after_nonstring() -> None:
    """Нестроковый элемент пропускается, а не обрывает весь список."""
    cleaned = drop_blank_aliases({'Brand': [None, 123, 'Bar', 'Бар']})
    assert cleaned == {'Brand': ['Bar', 'Бар']}


def test_drop_blank_aliases_keeps_brands_after_dict_entry() -> None:
    """Запись-словарь не обрывает разбор: следующие бренды тоже чистятся."""
    raw = {
        'Cordiant': {'aliases': ['', 'КОРДИАНТ'], 'group': 'cordiant'},
        'Kama': ['  ', 'Кама'],
        'Aeolus': '',
    }
    assert drop_blank_aliases(raw) == {
        'Cordiant': {'aliases': ['КОРДИАНТ'], 'group': 'cordiant'},
        'Kama': ['Кама'],
        'Aeolus': '',
    }


def test_drop_blank_aliases_missing_key_gets_empty_list() -> None:
    """У словаря без ключа aliases появляется пустой список, а не None."""
    cleaned = drop_blank_aliases({'Brand': {'group': 'brand'}})

    assert cleaned == {'Brand': {'aliases': [], 'group': 'brand'}}


def test_load_aliases_map_reads_file_of_passed_provider(tmp_path: Any) -> None:
    """Карта читается из файла переданного провайдера; разные провайдеры не смешиваются."""
    first, second = tmp_path / 'a.json', tmp_path / 'b.json'
    first.write_text('{"A": ["a"]}', encoding='utf-8')
    second.write_text('{"B": ["b"]}', encoding='utf-8')
    clear_manufacturer_aliases_cache()

    provider_a = MagicMock(config_file=MagicMock(return_value=str(first)))
    provider_b = MagicMock(config_file=MagicMock(return_value=str(second)))

    assert load_aliases_map(provider_a) == {'A': ['a']}
    assert load_aliases_map(provider_b) == {'B': ['b']}
    clear_manufacturer_aliases_cache()
