"""Сообщения сводки разбора: пропуски, расхождения, кириллические двойники.

Модуль собирает пары (уровень, текст); писать их в лог — задача оркестратора. Исключение — ошибка разбора:
её traceback пишется один раз здесь.
"""

import logging

from infrastructure.logging.exception_logging import log_exception_once
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.category_finder import skipped_unknown_categories_message
from parsers.data_provider.black_list import skipped_black_list_message
from parsers.strategies.product_types import type_corrections_message
from parsers.strategies.title_compose import titles_not_composed_message
from parsers.strategies.title_conflicts import title_conflicts_message
from services.parse_result import ParseResult

type LogMessage = tuple[int, str]


def log_parse_failure(target: logging.Logger, parser: BaseParser, exc: BaseException) -> None:
    """Записать ошибку разбора прайса поставщика: сообщение в консоль и файл, traceback только в файл."""
    log_exception_once(target, f'Ошибка разбора прайса поставщика {parser!r} // {exc}', exc)


def skips_messages(parse_result: ParseResult) -> list[LogMessage]:
    """Сводка по пропускам категорий, black_list и расхождениям типа и названия."""
    candidates: list[tuple[int, str | None]] = [
        (logging.WARNING, skipped_unknown_categories_message(parse_result.unknown_category_skips)),
        (logging.INFO, skipped_black_list_message(parse_result.black_list_skips)),
        (logging.INFO, type_corrections_message(parse_result.type_corrections)),
        (logging.WARNING, title_conflicts_message(parse_result.title_conflicts)),
    ]
    return [(level, text) for level, text in candidates if text is not None and text]


def parser_messages(parser: BaseParser) -> list[LogMessage]:
    """Сообщения по двойникам и несобранным названиям одного поставщика."""
    return [*_homoglyph_messages(parser), *_titles_not_composed_messages(parser)]


def _homoglyph_messages(parser: BaseParser) -> list[LogMessage]:
    """Сколько кириллических двойников исправлено у поставщика и сколько смесей оставлено в логе."""
    stats = parser.stats
    if not (stats.homoglyph_fixes or stats.homoglyph_suspects):
        return []
    text = (
        f'{parser!r}: кириллические двойники исправлены: {stats.homoglyph_fixes}, '
        f'не исправлено (смесь алфавитов): {stats.homoglyph_suspects}; подробности в логе'
    )
    return [(logging.INFO, text)]


def _titles_not_composed_messages(parser: BaseParser) -> list[LogMessage]:
    """Сколько названий шин и дисков не собрано из полей (остался нормализованный текст поставщика)."""
    message = titles_not_composed_message(parser.stats.titles_not_composed)
    return [(logging.WARNING, f'{parser!r}: {message}')] if message else []
