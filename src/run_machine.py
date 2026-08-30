"""JSON-режим CLI: разбор прайса и ответ в stdout."""

import time
from collections.abc import Callable

from cfg.zapaska_api import get_zapaska_api_config
from core.log_message import set_print_quiet
from parse_report import JsonReport, emit_json, empty_stats, error_payload, ok_payload
from parse_report_build import report_from_common
from parsers.all_vendors import all_vendors
from parsers.common_price import CommonPrice
from parsers.common_price_output import CommonPriceOut
from parsers.remote.zapaska_client import load_remote_vendor_data
from run_argv import DOUBLES, PARSE, ZAPASKA

_INTERRUPT = "interrupted"


def machine_json(command: str, *, all_result: bool = False) -> int:
    """Выполнить команду, JSON в stdout. Логи в этом режиме не печатаются."""
    set_print_quiet(True)
    code = _emit_command(command, all_result)
    set_print_quiet(False)
    return code


def _emit_command(command: str, all_result: bool) -> int:
    started = time.monotonic()
    code = 0
    try:
        payload = _handlers()[command](all_result)
    except KeyboardInterrupt:
        payload = error_payload(command, "KeyboardInterrupt", _INTERRUPT)
        code = 1
    except Exception as exc:
        payload = error_payload(command, type(exc).__name__, str(exc))
        code = 1
    emit_json(payload, elapsed=time.monotonic() - started)
    return code


def _handlers() -> dict[str, Callable[[bool], JsonReport]]:
    return {
        PARSE: _json_parse,
        DOUBLES: _json_doubles,
        ZAPASKA: _json_zapaska,
    }


def _parse_common() -> CommonPrice:
    common = CommonPrice()
    common.parse_all_vendors(all_vendors())
    return common


def _json_parse(all_result: bool) -> JsonReport:
    started = time.monotonic()
    common = _parse_common()
    files = CommonPriceOut(common.parsed_items).write_all_prices()
    return report_from_common(PARSE, common, files, time.monotonic() - started, all_result=all_result)


def _json_doubles(all_result: bool) -> JsonReport:
    started = time.monotonic()
    common = _parse_common()
    report_path = CommonPriceOut(common.parsed_items).write_doubles_report()
    return report_from_common(
        DOUBLES,
        common,
        [report_path],
        time.monotonic() - started,
        rows=[row for row in common.parsed_items if row.is_double or row.double_candidate],
        all_result=all_result,
    )


def _json_zapaska(_all_result: bool) -> JsonReport:
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
