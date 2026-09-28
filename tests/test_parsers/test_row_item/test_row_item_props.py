"""tests for RowItem helper properties"""

from parsers.row_item.row_item import FieldDescriptor, RowItem

_MD5_HEX_LEN = 32


def test_codes_unique() -> None:
    """codes собирает уникальные ненулевые коды"""
    row = RowItem({'code': '1', 'code_man': '1', 'code_art': '2'})
    assert set(row.codes) == {'1', '2'}


def test_hash_title_empty() -> None:
    """hash_title для пустого title"""
    assert RowItem({}).hash_title is None


def test_hash_title_filled() -> None:
    """hash_title для заполненного title"""
    title_hash = RowItem({'title': 'abc'}).hash_title
    assert title_hash is not None
    assert len(title_hash) == _MD5_HEX_LEN


def test_from_dict_roundtrip() -> None:
    """сериализация через from_dict / to_dict"""
    row = RowItem.from_dict('{"title": "t1", "price_opt": 10}')
    assert row.title == 't1'
    assert row.to_dict()['title'] == 't1'


def test_field_descriptor_stores_name() -> None:
    descriptor = FieldDescriptor[str]('title')
    assert descriptor.name == 'title'


def test_field_descriptor_set_handles_value_error() -> None:
    """FieldDescriptor.__set__ записывает ошибку в _errors при ValueError."""
    row = RowItem({})
    row.price_opt = 'не число'
    assert 'price_opt' in row._errors
    assert 'не число' in row._errors['price_opt']['value']
    assert isinstance(row._errors['price_opt']['error'], str)


def test_field_descriptor_error_dict_keys_are_exact() -> None:
    """Запись об ошибке имеет ровно ключи 'value' и 'error': потребитель читает их по имени."""
    row = RowItem({})
    row.price_opt = 'не число'
    assert set(row._errors['price_opt']) == {'value', 'error'}


def test_row_item_from_raw_row_keeps_error_keys() -> None:
    """Сырая строка с битым полем: в parse_errors остаются ключи 'value' и 'error'."""
    row = RowItem({'price_opt': 'не число', 'title': 't1'})
    assert set(row.parse_errors) == {'price_opt'}
    assert set(row.parse_errors['price_opt']) == {'value', 'error'}
    assert row.parse_errors['price_opt']['value'] == 'не число'
