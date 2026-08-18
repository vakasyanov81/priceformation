"""
tests find category in title
"""

from typing import Any

import pytest

from parsers.base_parser.category_finder import (
    CategoryFinder,
    canonical_product_type,
    raw_category_label,
    skipped_unknown_categories_message,
)
from parsers.row_item.row_item import RowItem


@pytest.mark.parametrize(
    "title, category",
    [
        ("bla bla автошина bla", "Автошина"),
        ("bla bla шина bla", "Автошина"),
        ("bla bla шины bla", "Автошина"),
        ("bla bla диски bla", "Диск"),
        ("bla bla диск bla", "Диск"),
        ("bla bla автодиск bla", "Диск"),
        ("bla bla автодиски bla", "Диск"),
        ("bla bla камеры bla", "Автокамера"),
        ("bla bla камера bla", "Автокамера"),
        ("bla bla камера bla Алтайшина", "Автокамера"),
        ("bla bla ободная лента bla", "Ободная лента"),
        ("bla bla Ободная лента bla", "Ободная лента"),
    ],
)
def test_find_category_from_title(title: Any, category: Any) -> None:
    """test find category"""

    row_item = RowItem({"title": title})

    found_category, _ = CategoryFinder().find(row_item)
    assert found_category == category


@pytest.mark.parametrize(
    ("raw_type", "expected"),
    [
        ("Грузовая", "Грузовая шина"),
        ("  легковая  ", "Легковая шина"),
        ("Легковая шина", "Легковая шина"),
        ("легкогрузовая", "Легковая шина"),
        ("сельхоз", "Спецшина"),
        ("мотошина", "Мотошина"),
        ("Диск", "Диск"),
    ],
)
def test_canonical_product_type_known(raw_type: str, expected: str) -> None:
    """известные категории поставщика мапятся на канонический тип"""
    assert canonical_product_type(raw_type) == expected


@pytest.mark.parametrize(
    "raw_type",
    [None, "", "  ", "SUV", "неизвестно"],
)
def test_canonical_product_type_unknown(raw_type: str | None) -> None:
    """неизвестная или пустая категория не мапится"""
    assert canonical_product_type(raw_type) is None


@pytest.mark.parametrize(
    ("raw_type", "expected"),
    [
        (None, "не указан"),
        ("", "не указан"),
        ("  ", "не указан"),
        ("SUV", "SUV"),
        ("  SUV  ", "SUV"),
    ],
)
def test_raw_category_label(raw_type: str | None, expected: str) -> None:
    """подпись неизвестной категории для отчёта о пропусках"""
    assert raw_category_label(raw_type) == expected


def test_skipped_unknown_categories_message_empty() -> None:
    """без пропусков сообщение не строится"""
    assert skipped_unknown_categories_message([]) is None


def test_skipped_unknown_categories_message() -> None:
    """сводка считает позиции и собирает поставщиков с категориями"""
    message = skipped_unknown_categories_message(
        [
            ("Запаска (шины)", "SUV"),
            ("Запаска (шины)", "SUV"),
            ("Другой", "Foo"),
        ],
    )
    assert message is not None
    assert "Пропущено 3 позиций" in message
    assert "Другой, Запаска (шины)" in message
    assert "Foo, SUV" in message
