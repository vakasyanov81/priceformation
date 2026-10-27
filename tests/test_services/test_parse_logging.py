"""parse_logging: сообщения сводки разбора собираются парами (уровень, текст)."""

import logging
from types import SimpleNamespace
from typing import Any, cast

from parsers.base_parser.base_parser import BaseParser
from services.parse_logging import parser_messages, skips_messages
from services.parse_result import ParseResult


def _parser(**stats: int) -> BaseParser:
    """Парсер-заглушка со счётчиками; пропущенные счётчики равны нулю."""
    counters = {'homoglyph_fixes': 0, 'homoglyph_suspects': 0, 'titles_not_composed': 0, **stats}
    fake: Any = SimpleNamespace(stats=SimpleNamespace(**counters), __repr__=lambda: 'P')
    return cast(BaseParser, fake)


def test_skips_messages_empty_result_has_no_messages() -> None:
    """Пустой результат разбора — сводки нет."""
    assert skips_messages(ParseResult()) == []


def test_skips_messages_black_list_is_info() -> None:
    """Пропуски black_list идут уровнем INFO."""
    messages = skips_messages(ParseResult(black_list_skips=3))

    assert [level for level, _ in messages] == [logging.INFO]


def test_skips_messages_title_conflicts_is_warning() -> None:
    """Конфликты названий идут уровнем WARNING."""
    messages = skips_messages(ParseResult(title_conflicts=2))

    assert [level for level, _ in messages] == [logging.WARNING]


def test_parser_messages_clean_parser_has_no_messages() -> None:
    """Без двойников и несобранных названий сообщений нет."""
    assert parser_messages(_parser()) == []


def test_parser_messages_homoglyphs_then_titles() -> None:
    """Сначала двойники (INFO), затем несобранные названия (WARNING)."""
    messages = parser_messages(_parser(homoglyph_fixes=2, homoglyph_suspects=1, titles_not_composed=4))

    assert [level for level, _ in messages] == [logging.INFO, logging.WARNING]
    assert 'исправлены: 2' in messages[0][1]
    assert 'смесь алфавитов): 1' in messages[0][1]
