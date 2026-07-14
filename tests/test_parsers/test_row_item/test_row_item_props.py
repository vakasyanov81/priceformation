"""tests for RowItem helper properties"""

from parsers.row_item.row_item import RowItem

_MD5_HEX_LEN = 32


def test_codes_unique():
    """codes собирает уникальные ненулевые коды"""
    row = RowItem({"code": "1", "code_man": "1", "code_art": "2"})
    assert set(row.codes) == {"1", "2"}


def test_hash_title_empty():
    """hash_title для пустого title"""
    assert RowItem({}).hash_title is None


def test_hash_title_filled():
    """hash_title для заполненного title"""
    title_hash = RowItem({"title": "abc"}).hash_title
    assert title_hash is not None
    assert len(title_hash) == _MD5_HEX_LEN


def test_from_dict_roundtrip():
    """сериализация через from_dict / to_dict"""
    row = RowItem.from_dict('{"title": "t1", "price_opt": 10}')
    assert row.title == "t1"
    assert row.to_dict()["title"] == "t1"
