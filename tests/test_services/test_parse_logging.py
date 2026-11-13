"""parse_logging: сообщения сводки разбора собираются парами (уровень, текст)."""

import logging
from types import SimpleNamespace
from typing import Any, cast

import pytest

from domain.product_groups import ProductGroup
from parsers.base_parser.base_parser import BaseParser
from services.parse_logging import parser_messages, skips_messages
from services.parse_result import ParseResult
from services.parse_statistics import GroupStatistics, TireAndDiskDiagnostics


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
    messages = skips_messages(ParseResult(statistics={ProductGroup.TIRE_AND_DISK: GroupStatistics(black_list_skips=3)}))

    assert [level for level, _ in messages] == [logging.INFO]


def test_skips_messages_title_conflicts_is_warning() -> None:
    """Конфликты названий идут уровнем WARNING."""
    messages = skips_messages(ParseResult(tire_and_disk_diagnostics=TireAndDiskDiagnostics(title_conflicts=2)))

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


@pytest.mark.parametrize(
    ('stats', 'expected'),
    [
        ({'homoglyph_fixes': 2}, 'исправлены: 2, не исправлено (смесь алфавитов): 0'),
        ({'homoglyph_suspects': 3}, 'исправлены: 0, не исправлено (смесь алфавитов): 3'),
    ],
)
def test_parser_messages_homoglyph_counter_is_independent(stats: dict[str, int], expected: str) -> None:
    messages = parser_messages(_parser(**stats))

    assert len(messages) == 1
    assert expected in messages[0][1]


def test_foreign_group_does_not_receive_tire_diagnostics() -> None:
    """Чужая группа не получает даже случайно переданные шинные счётчики."""
    parser = _parser(homoglyph_fixes=2, titles_not_composed=4)
    assert parser_messages(parser, ProductGroup.BATTERIES) == []


def test_black_list_messages_identify_each_group() -> None:
    """Общий счётчик пропусков сопровождается идентификатором своей группы."""
    parsed = ParseResult(
        statistics={
            ProductGroup.TIRE_AND_DISK: GroupStatistics(black_list_skips=2),
            ProductGroup.BATTERIES: GroupStatistics(black_list_skips=3),
        }
    )

    messages = skips_messages(parsed)

    assert len(messages) == 2
    assert messages[0][1].startswith('[tire_and_disk]')
    assert messages[1][1].startswith('[batteries]')
