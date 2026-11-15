"""Начальное заполнение VO сохраняет контракт последовательной записи полей."""

from typing import Any
from unittest.mock import patch

import pytest

from domain.row_item.field_registry import FIELD_KEYS
from domain.row_item.row_item import RowItem

_RAW_ROWS: tuple[dict[str, Any], ...] = (
    {},
    dict.fromkeys(FIELD_KEYS, '12'),
    {'warehouse_name': '  Новосибирск  ', 'warehouse_id': 'bad', 'price_opt': 'bad', 'extra': ' x '},
    {'title': None, 'price_opt': None, 'rest_count': 0, 'marked_down': False, 'extra': None},
)


@pytest.mark.parametrize('raw', _RAW_ROWS)
def test_initialization_matches_sequential_writes(raw: dict[str, Any]) -> None:
    """Дефолты, ошибки, extra и порядок ключей совпадают с публичной записью."""
    expected = RowItem()
    for key, raw_value in raw.items():
        expected.set_field(key, raw_value)
    actual = RowItem(raw)

    assert actual.to_dict() == expected.to_dict()
    assert list(actual.to_dict()) == list(expected.to_dict())
    assert actual.parse_errors == expected.parse_errors
    assert actual.extra == expected.extra
    for group in ('identity', 'tire', 'disk', 'pricing', 'stock', 'duplicate', 'vendor'):
        assert getattr(actual, group) == getattr(expected, group)


def test_initialization_does_not_replace_empty_value_objects() -> None:
    """Заполненные VO собираются сразу: replace нужен только для последующих изменений."""
    with patch('domain.row_item.row_item.replace', side_effect=AssertionError('лишний replace')):
        row = RowItem(dict.fromkeys(FIELD_KEYS, '12'))
    assert row.stock.warehouse_id == 12
