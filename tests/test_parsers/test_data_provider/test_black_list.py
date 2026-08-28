"""tests for black list split helper and glob masks"""

from typing import Any

import pytest

from parsers.data_provider.black_list import (
    BlackListProviderFromUserConfig,
    skipped_black_list_message,
    split_exact_and_masks,
    title_matches_mask,
)


def test_split_black_list() -> None:
    """split and strip lines from raw text"""
    assert BlackListProviderFromUserConfig().split_and_filtration("test1\n test2") == ["test1", "test2"]


def test_split_keeps_spaces_inside_line() -> None:
    """пробел внутри строки не является разделителем"""
    assert BlackListProviderFromUserConfig.split_and_filtration("foo bar\nbaz") == ["foo bar", "baz"]


def test_split_exact_and_masks() -> None:
    titles, masks = split_exact_and_masks(
        ["Основание обода", "*некондиция*", "другой товар", "*2 сорт*"],
    )
    assert titles == ["Основание обода", "другой товар"]
    assert masks == ["*некондиция*", "*2 сорт*"]


@pytest.mark.parametrize(
    ("title", "mask", "expected"),
    [
        ("some некондиция product", "*некондиция*", True),
        ("НЕКОНДИЦИЯ", "*некондиция*", True),
        ("ok title", "*некондиция*", False),
        ("восстановленная шина", "восстановленная*", True),
        ("не восстановленная", "восстановленная*", False),
        ("товар 2 сорт", "*2 сорт", True),
        ("2 сорт товар", "*2 сорт", False),
        ("exact", "exact", True),
        ("exact extra", "exact", False),
    ],
)
def test_title_matches_mask(title: Any, mask: Any, expected: Any) -> None:
    assert title_matches_mask(title, mask) is expected


def test_skipped_black_list_message_empty() -> None:
    assert skipped_black_list_message(0) is None


def test_skipped_black_list_message() -> None:
    message = skipped_black_list_message(3)
    assert message is not None
    assert "Отброшено 3 позиций по правилам black_list." in message
