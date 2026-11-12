"""JSON-отчёт разбора прайса для сторонних скриптов (Django и др.)."""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Mapping
from typing import Any, TextIO

from app.parse_report_types import JsonError, JsonGroup, JsonReport

REPORT_VERSION = 2
_OK_KEY = 'ok'


def dump_json(payload: Mapping[str, Any]) -> str:
    """Сериализовать отчёт в одну JSON-строку."""
    return json.dumps(payload, ensure_ascii=False, default=str)


def emit_json(
    payload: Mapping[str, Any],
    stream: TextIO | None = None,
    *,
    started: float | None = None,
) -> None:
    """Печать JSON в stdout (или переданный поток). started — monotonic, добавляет elapsed_seconds."""
    report: Mapping[str, Any] = payload
    if started is not None and _OK_KEY in payload:
        report = {**payload, 'elapsed_seconds': round(time.monotonic() - started, 2)}
    print(dump_json(report), file=stream or sys.stdout, flush=True)


def empty_stats(elapsed: float) -> dict[str, Any]:
    """Нулевая статистика той же формы, что у разбора."""
    return {
        'items': 0,
        'priced_items': 0,
        'doubles': 0,
        'black_list_skips': 0,
        'unrouted_rows': 0,
        'elapsed_seconds': round(elapsed, 2),
    }


def ok_payload(
    *,
    action: str,
    groups: dict[str, JsonGroup],
    stats: dict[str, Any],
    warnings: list[str],
    files: list[str],
    suppliers: dict[str, str],
) -> JsonReport:
    """Собрать успешный ответ."""
    return {
        'ok': True,
        'version': REPORT_VERSION,
        'action': action,
        'groups': groups,
        'stats': stats,
        'warnings': warnings,
        'files': files,
        'suppliers': suppliers,
        'disabled_suppliers': {},
        'error': None,
    }


def error_payload(
    action: str,
    kind: str,
    message: str,
    *,
    compact: bool = False,
    groups: tuple[str, ...] = (),
) -> Mapping[str, Any]:
    """Собрать ответ об ошибке. compact — только ok/action/error (не разбор)."""
    error: JsonError = {'kind': kind, 'message': message}
    if compact:
        return {_OK_KEY: False, 'action': action, 'error': error}
    return {
        'ok': False,
        'version': REPORT_VERSION,
        'action': action,
        'groups': {
            group: {
                'positions': [],
                'stats': dict.fromkeys(('items', 'priced_items', 'doubles', 'black_list_skips'), 0),
            }
            for group in groups
        },
        'stats': empty_stats(0),
        'warnings': [],
        'files': [],
        'suppliers': {},
        'disabled_suppliers': {},
        'error': error,
    }
