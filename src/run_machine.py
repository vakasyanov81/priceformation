"""JSON-режим CLI: разбор прайса и ответ в stdout."""

import logging
import time
from collections.abc import Callable

from cfg.zapaska_api import get_zapaska_api_config
from core.log_message import print_log, set_print_quiet
from parse_report import JsonReport, emit_json, empty_stats, error_payload, ok_payload
from parse_report_build import report_from_common
from parsers.all_vendors import all_vendors
from parsers.common_price import CommonPrice
from parsers.common_price_output import CommonPriceOut
from parsers.remote.zapaska_client import load_remote_vendor_data
from parsers.writer.templates.all_templates import UnknownWriterTemplateError, get_writer_template
from run_argv import DOUBLES, PARSE, ZAPASKA

_INTERRUPT = "interrupted"


def fail_unknown_result_template(
    command: str,
    name: str | None,
    *,
    json_mode: bool,
) -> int | None:
    """Если имя шаблона задано и неизвестно — ответ с ошибкой и код 1."""
    if name is None:
        return None
    try:
        get_writer_template(name)
    except UnknownWriterTemplateError as exc:
        if json_mode:
            emit_json(error_payload(command, type(exc).__name__, str(exc)))
        else:
            print_log(str(exc), level=logging.ERROR)
        return 1
    return None


def machine_json(
    command: str,
    *,
    all_result: bool = False,
    result_template: str | None = None,
) -> int:
    """Выполнить команду, JSON в stdout. Логи в этом режиме не печатаются."""
    set_print_quiet(True)
    code = _emit_command(command, all_result, result_template)
    set_print_quiet(False)
    return code


def _emit_command(command: str, all_result: bool, result_template: str | None) -> int:
    handlers: dict[str, Callable[[bool, str | None], JsonReport]] = {
        PARSE: _json_parse,
        DOUBLES: _json_doubles,
        ZAPASKA: _json_zapaska,
    }
    try:
        payload = handlers[command](all_result, result_template)
    except KeyboardInterrupt:
        emit_json(error_payload(command, "KeyboardInterrupt", _INTERRUPT))
        return 1
    except Exception as exc:
        emit_json(error_payload(command, type(exc).__name__, str(exc)))
        return 1
    emit_json(payload)
    return 0


def _parse_common() -> CommonPrice:
    common = CommonPrice()
    common.parse_all_vendors(all_vendors())
    return common


def _json_parse(all_result: bool, result_template: str | None) -> JsonReport:
    started = time.monotonic()
    common = _parse_common()
    files = CommonPriceOut(common.parsed_items).write_all_prices(
        as_jsonl=True,
        result_template=result_template,
    )
    return report_from_common(PARSE, common, files, time.monotonic() - started, all_result=all_result)


def _json_doubles(all_result: bool, _result_template: str | None) -> JsonReport:
    started = time.monotonic()
    common = _parse_common()
    report_path = CommonPriceOut(common.parsed_items).write_doubles_report(as_jsonl=True)
    return report_from_common(
        DOUBLES,
        common,
        [report_path],
        time.monotonic() - started,
        rows=[row for row in common.parsed_items if row.is_double or row.double_candidate],
        all_result=all_result,
    )


def _json_zapaska(_all_result: bool, _result_template: str | None) -> JsonReport:
    started = time.monotonic()
    load_remote_vendor_data(api=get_zapaska_api_config())
    return ok_payload(
        action=ZAPASKA,
        positions=[],
        stats=empty_stats(time.monotonic() - started),
        warnings=[],
        files=[],
        suppliers={},
    )
