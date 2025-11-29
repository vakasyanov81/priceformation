# -*- coding: utf-8 -*-
"""
tests find category in title
"""
__author__ = "Kasyanov V.A."

import pytest

from parsers.base_parser.category_finder import CategoryFinder
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
def test_find_category_from_title(title, category):
    """test find category"""

    item = RowItem({"title": title})

    found_category, _ = CategoryFinder().find(item)
    assert found_category == category
