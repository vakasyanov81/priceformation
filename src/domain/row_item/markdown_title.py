"""Признак уценки по названию позиции."""

import re

_MARKDOWN_RE = re.compile(r'уцен|дефект', re.IGNORECASE)


def is_markdown_title(title: str | None) -> bool:
    """Уценённый товар: в названии «Уценка», «уценённый», «Дефект ЛКП»."""
    return bool(title) and _MARKDOWN_RE.search(title or '') is not None
