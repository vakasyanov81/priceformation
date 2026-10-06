"""Чтение примитивов из JSON-конфига поставщика."""

import pytest

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.fields import read_int, read_int_list, read_str_list, read_str_map, read_text

WHERE = 'mim.json'


def test_read_text_returns_value() -> None:
    assert read_text({'name': 'Мим'}, 'name', WHERE) == 'Мим'


def test_read_text_requires_key() -> None:
    with pytest.raises(ConfigValidationError, match='отсутствует обязательный ключ'):
        read_text({'name': 'Мим'}, 'code', WHERE)


def test_read_text_returns_default_for_missing_key() -> None:
    assert read_text({'name': 'Мим'}, 'code', WHERE, '') == ''


def test_read_text_rejects_non_string() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается строка'):
        read_text({'name': 5}, 'name', WHERE)


def test_read_text_rejects_blank_required_value() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается непустая строка'):
        read_text({'name': '   '}, 'name', WHERE)


def test_read_text_allows_blank_optional_value() -> None:
    assert read_text({'name': '   '}, 'name', WHERE, '') == '   '


def test_read_int_returns_value() -> None:
    assert read_int({'start_row': 3}, 'start_row', WHERE) == 3


def test_read_int_requires_key() -> None:
    with pytest.raises(ConfigValidationError, match='отсутствует обязательный ключ'):
        read_int({}, 'start_row', WHERE)


def test_read_int_returns_default_for_missing_key() -> None:
    assert read_int({}, 'start_row', WHERE, 4) == 4


def test_read_int_accepts_whole_float() -> None:
    assert read_int({'start_row': 3.0}, 'start_row', WHERE) == 3


def test_read_int_rejects_bool() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается целое'):
        read_int({'start_row': True}, 'start_row', WHERE)


def test_read_int_rejects_fractional_number() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается целое'):
        read_int({'start_row': 3.5}, 'start_row', WHERE)


def test_read_str_list_returns_tuple() -> None:
    assert read_str_list({'files': ['a', 'b']}, 'files', WHERE) == ('a', 'b')


def test_read_str_list_requires_key() -> None:
    with pytest.raises(ConfigValidationError, match='отсутствует обязательный ключ'):
        read_str_list({}, 'files', WHERE)


def test_read_str_list_returns_default_for_missing_key() -> None:
    assert read_str_list({}, 'files', WHERE, ()) == ()


def test_read_str_list_rejects_non_list() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается список строк'):
        read_str_list({'files': 'a'}, 'files', WHERE)


def test_read_str_list_rejects_non_string_entry() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается список строк'):
        read_str_list({'files': ['a', 1]}, 'files', WHERE)


def test_read_int_list_returns_tuple() -> None:
    assert read_int_list({'sheets': [0, 1]}, 'sheets', WHERE) == (0, 1)


def test_read_int_list_returns_empty_for_missing_key() -> None:
    assert read_int_list({}, 'sheets', WHERE) == ()


def test_read_int_list_rejects_non_list() -> None:
    with pytest.raises(ConfigValidationError, match='должно быть списком'):
        read_int_list({'sheets': 3}, 'sheets', WHERE)


def test_read_int_list_rejects_non_integer_entry() -> None:
    with pytest.raises(ConfigValidationError, match='ожидается целое'):
        read_int_list({'sheets': [0, 'x']}, 'sheets', WHERE)


def test_read_str_map_returns_mapping() -> None:
    assert read_str_map({'columns': {'0': 'Код'}}, 'columns', WHERE) == {'0': 'Код'}


def test_read_str_map_returns_empty_for_missing_key() -> None:
    assert read_str_map({}, 'columns', WHERE) == {}


def test_read_str_map_rejects_non_object() -> None:
    with pytest.raises(ConfigValidationError, match='должно быть объектом строк'):
        read_str_map({'columns': []}, 'columns', WHERE)


def test_read_str_map_rejects_non_string_value() -> None:
    with pytest.raises(ConfigValidationError, match='должно быть объектом строк'):
        read_str_map({'columns': {'0': 1}}, 'columns', WHERE)
