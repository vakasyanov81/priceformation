"""tests for RowItem helper properties"""

import pytest

from parsers.row_item.row_item import RowField, RowItem
from parsers.row_item.value_objects import (
    DiskParameters,
    DuplicateInfo,
    Pricing,
    ProductIdentity,
    Stock,
    TireDimensions,
    VendorMeta,
)

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


def test_to_dict_roundtrip() -> None:
    """позиция строится из плоского словаря и отдаёт его же"""
    row = RowItem({'title': 't1', 'price_opt': 10})
    assert row.identity.title == 't1'
    assert row.to_dict()['title'] == 't1'


def test_row_field_stores_name() -> None:
    """RowField отдаёт имя плоского ключа по классу, а не по позиции."""
    assert RowField('title').name == 'title'
    assert RowItem.title.name == 'title'
    assert RowItem.manufacturer.name == 'manufacturer_name'


def test_row_field_rejects_unknown_key() -> None:
    """RowField без описания в реестре — ошибка на этапе импорта класса."""
    with pytest.raises(KeyError) as err:
        RowField('hash_title')

    assert err.value.args == ('hash_title',)


def test_flat_access_from_item_is_refused() -> None:
    """Плоский доступ с позиции снят: вместо значения он вернул бы молча ключ."""
    row = RowItem({'title': 't1'})

    with pytest.raises(AttributeError, match='Плоский доступ поля снят'):
        RowItem.title.__get__(row)

    with pytest.raises(AttributeError, match='Плоский доступ поля снят'):
        RowItem.title.__set__(row, 't2')


def test_row_field_set_handles_value_error() -> None:
    """Запись через RowField пишет ошибку в _errors при ValueError."""
    row = RowItem({})
    row.set_field('price_opt', 'не число')
    assert 'price_opt' in row._errors
    assert 'не число' in row._errors['price_opt']['value']
    assert isinstance(row._errors['price_opt']['error'], str)


def test_row_field_error_dict_keys_are_exact() -> None:
    """Запись об ошибке имеет ровно ключи 'value' и 'error': потребитель читает их по имени."""
    row = RowItem({})
    row.set_field('price_opt', 'не число')
    assert set(row._errors['price_opt']) == {'value', 'error'}


def test_row_item_from_raw_row_keeps_error_keys() -> None:
    """Сырая строка с битым полем: в parse_errors остаются ключи 'value' и 'error'."""
    row = RowItem({'price_opt': 'не число', 'title': 't1'})
    assert set(row.parse_errors) == {'price_opt'}
    assert set(row.parse_errors['price_opt']) == {'value', 'error'}
    assert row.parse_errors['price_opt']['value'] == 'не число'


def test_parse_errors_returns_copy() -> None:
    """Потребитель не может дописать во внутренний словарь ошибок."""
    row = RowItem({'price_opt': 'не число'})

    errors = row.parse_errors
    errors['price_opt'] = 'подмена'
    errors['hash_title'] = {'value': 'x', 'error': 'y'}

    assert set(row.parse_errors) == {'price_opt'}
    assert row.parse_errors['price_opt']['error'] != 'подмена'


def test_value_objects_are_filled_by_key() -> None:
    """плоский ключ попадает в value object по пути из реестра."""
    raw = {'title': 't1', 'width': '225', 'pcd1': '114.3', 'price_opt': '10', 'rest_count': '5'}
    row = RowItem(raw)
    assert row.identity == ProductIdentity(title='t1')
    assert row.tire == TireDimensions(width='225')
    assert row.disk == DiskParameters(pcd1=114.3)
    assert row.pricing == Pricing(price_opt=10)
    assert row.stock == Stock(rest_count=5)
    assert row.duplicate == DuplicateInfo()
    assert row.vendor == VendorMeta()


def test_unset_fields_read_as_registry_default() -> None:
    """незаданное поле читается как дефолт реестра, а не как пустое значение."""
    row = RowItem({})
    assert row.pricing.price_opt == 0
    assert row.pricing.price_markup == 0
    assert row.tire.width is None
    assert row.disk.pcd1 is None


def test_vendor_keys_stay_in_extra() -> None:
    """ключ без описания в реестре едет в extra и возвращается в to_dict."""
    row = RowItem({'hash_title': 'deadbeef'})
    assert row.extra == {'hash_title': 'deadbeef'}
    assert row.to_dict() == {'hash_title': 'deadbeef'}


def test_set_field_keeps_first_key_position() -> None:
    """повторная запись поля не меняет его места в плоском словаре."""
    row = RowItem({'title': 't1', 'width': '225'})
    row.set_field('title', 't2')
    row.set_field('season', 'Зима')
    assert list(row.to_dict()) == ['title', 'width', 'season']
    assert row.to_dict()['title'] == 't2'


def test_set_keys_keep_only_keys_in_write_order() -> None:
    """_set_keys — упорядоченное множество заданных ключей, значения не несут."""
    row = RowItem({'title': 't1'})
    row.set_field('width', '225')
    row.set_field('title', 't2')
    assert row._set_keys == {'title': None, 'width': None}


def test_set_field_keeps_explicit_none() -> None:
    """явно заданный None остаётся ключом плоского словаря."""
    row = RowItem({'ext_diameter': None})
    assert row.to_dict() == {'ext_diameter': None}


def test_failed_conversion_leaves_previous_value() -> None:
    """неудачная запись не затирает уже приведённое значение."""
    row = RowItem({'price_opt': '10'})
    row.set_field('price_opt', 'не число')
    assert row.pricing.price_opt == 10
    assert 'price_opt' in row.parse_errors


def test_row_item_is_not_compared_by_fields() -> None:
    """две одинаковые позиции остаются разными объектами."""
    assert RowItem({'title': 't1'}) != RowItem({'title': 't1'})
