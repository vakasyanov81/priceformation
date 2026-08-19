"""Helpers for preparing and filtering parser row items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from core import err_msg
from parsers.row_item.row_item import RowItem

if TYPE_CHECKING:
    from parsers.base_parser.base_parser import BaseParser


def _set_title_or_log(parser: BaseParser, row_id: int, row_item: RowItem) -> bool:
    """Собрать title; при ValueError — лог и False."""
    try:
        parser.set_prepared_title(row_item)
    except ValueError as err:
        err_msg(
            f"Не удалось разобрать строку (№ {row_id}) у поставщика: {repr(parser)} // {err}",
            need_print_log=True,
        )
        err_msg(f"строка: {repr(row_item)}")
        return False
    return True


def _log_row_parse_errors(parser: BaseParser, row_id: int, row_item: RowItem) -> None:
    """Лог ошибок разбора полей строки."""
    err_msg(
        f"Не удалось разобрать строку (№ {row_id}) у поставщика: {repr(parser)} // {row_item.parse_errors}",
        need_print_log=True,
    )
    err_msg(f"строка: {repr(row_item.to_dict())}")


def _enrich_row_item(parser: BaseParser, row_item: RowItem) -> RowItem:
    """Производитель, категория, служебные поля."""
    parser.manufacturer_finder().process(row_item)
    parser.correction_category(row_item)
    row_item.supplier_name = parser.parser_params().supplier.name
    row_item.spike = parser.get_spike_title(row_item)
    row_item.season = parser.replace_season(row_item)
    return row_item


def _try_prepare_row(parser: BaseParser, row_id: int, row_item: RowItem) -> RowItem | None:
    """Подготовить одну строку или вернуть None при ошибке/фильтре."""
    if not _set_title_or_log(parser, row_id, row_item):
        return None
    if row_item.parse_errors:
        _log_row_parse_errors(parser, row_id, row_item)
        return None
    if not parser.is_valid_title(row_item.title):
        return None
    return _enrich_row_item(parser, row_item)


def _keep_row_item(parser: BaseParser, row_item: RowItem) -> bool:
    """Оставить строку с ценой закупки и валидным title."""
    if row_item.rest_count and not row_item.price_opt:
        return False
    if row_item.title and not parser.is_valid_title(row_item.title):
        return False
    return True
