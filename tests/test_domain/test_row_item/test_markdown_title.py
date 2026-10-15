"""Признак уценки по названию."""

import pytest

from domain.row_item.markdown_title import is_markdown_title


@pytest.mark.parametrize(
    'title',
    ['13 Trebl 5.0*13 S паллета Уценка Дефект ЛКП', 'Шина 205/55R16 уценённая', 'Диск Дефект покраски'],
)
def test_markdown_titles(title: str) -> None:
    assert is_markdown_title(title)


@pytest.mark.parametrize('title', ['13 Trebl 5.0*13 S паллета', '', None])
def test_regular_titles(title: str | None) -> None:
    assert not is_markdown_title(title)
