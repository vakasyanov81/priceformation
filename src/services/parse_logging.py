"""Сообщения сводки разбора: пропуски, расхождения, кириллические двойники.

Модуль собирает пары (уровень, текст); писать их в лог — задача оркестратора. Исключение — ошибка разбора:
её traceback пишется один раз здесь.
"""

import logging

from domain.product_groups import ProductGroup
from infrastructure.logging.exception_logging import log_exception_once
from parsers.base_parser.category_finder import skipped_unknown_categories_message
from parsers.base_parser.supplier_parser import SupplierParser
from parsers.data_provider.black_list import skipped_black_list_message
from parsers.strategies.product_types import type_corrections_message
from parsers.strategies.title_compose import titles_not_composed_message
from parsers.strategies.title_conflicts import title_conflicts_message
from services.parse_result import ParseResult

type LogMessage = tuple[int, str]


def log_parse_failure(target: logging.Logger, parser: SupplierParser, exc: BaseException) -> None:
    """Записать ошибку разбора прайса поставщика: сообщение в консоль и файл, traceback только в файл."""
    group = parser.product_group.value
    context = f'{parser!r} [{group}]'
    log_exception_once(target, f'Ошибка разбора прайса поставщика {context} // {exc}', exc)


def skips_messages(parse_result: ParseResult) -> list[LogMessage]:
    """Сводка по пропускам категорий, black_list и расхождениям типа и названия."""
    diagnostics = parse_result.tire_and_disk_diagnostics
    candidates: list[tuple[int, str | None]] = [
        (logging.WARNING, skipped_unknown_categories_message(diagnostics.unknown_category_skips)),
        (logging.INFO, type_corrections_message(diagnostics.type_corrections)),
        (logging.WARNING, title_conflicts_message(diagnostics.title_conflicts)),
    ]
    messages = [(level, f'[tire_and_disk] {text}') for level, text in candidates if text]
    return messages + _black_list_messages(parse_result)


def _black_list_messages(parse_result: ParseResult) -> list[LogMessage]:
    """Общие пропуски не требуют полей шинной модели."""
    messages: list[LogMessage] = []
    for group, counters in parse_result.statistics.items():
        black_list = skipped_black_list_message(counters.black_list_skips)
        if black_list:
            messages.append((logging.INFO, f'[{group.value}] {black_list}'))
    return messages


def parser_messages(parser: SupplierParser, group: ProductGroup = ProductGroup.TIRE_AND_DISK) -> list[LogMessage]:
    """Сообщения по двойникам и несобранным названиям одного поставщика."""
    if group is not ProductGroup.TIRE_AND_DISK:
        return []
    messages = [*_homoglyph_messages(parser), *_titles_not_composed_messages(parser)]
    return [(level, f'[{group.value}] {text}') for level, text in messages]


def _homoglyph_messages(parser: SupplierParser) -> list[LogMessage]:
    """Сколько кириллических двойников исправлено у поставщика и сколько смесей оставлено в логе."""
    stats = parser.stats
    if not (stats.homoglyph_fixes or stats.homoglyph_suspects):
        return []
    text = (
        f'{parser!r}: кириллические двойники исправлены: {stats.homoglyph_fixes}, '
        f'не исправлено (смесь алфавитов): {stats.homoglyph_suspects}; подробности в логе'
    )
    return [(logging.INFO, text)]


def _titles_not_composed_messages(parser: SupplierParser) -> list[LogMessage]:
    """Сколько названий шин и дисков не собрано из полей (остался нормализованный текст поставщика)."""
    message = titles_not_composed_message(parser.stats.titles_not_composed)
    return [(logging.WARNING, f'{parser!r}: {message}')] if message else []
