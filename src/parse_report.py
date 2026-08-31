"""JSON-отчёт разбора прайса для сторонних скриптов (Django и др.)."""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Mapping
from typing import Any, TextIO, TypedDict

REPORT_VERSION = 1
_OK_KEY = "ok"


class JsonError(TypedDict):
    """Ошибка запуска."""

    kind: str
    message: str


class JsonReport(TypedDict):
    """Стабильная схема ответа CLI."""

    ok: bool
    version: int
    action: str
    positions: list[dict[str, Any]]
    stats: dict[str, Any]
    warnings: list[str]
    files: list[str]
    suppliers: dict[str, str]
    disabled_suppliers: dict[str, str]
    error: JsonError | None


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
        report = {**payload, "elapsed_seconds": round(time.monotonic() - started, 2)}
    print(dump_json(report), file=stream or sys.stdout, flush=True)


def empty_stats(elapsed: float) -> dict[str, Any]:
    """Нулевая статистика той же формы, что у разбора."""
    return {
        "items": 0,
        "priced_items": 0,
        "doubles": 0,
        "unknown_category_skips": 0,
        "black_list_skips": 0,
        "elapsed_seconds": round(elapsed, 2),
        "percent_markup": {"min": 0, "max": 0},
        "absolute_markup": {"min": 0, "max": 0},
    }


def ok_payload(
    *,
    action: str,
    positions: list[dict[str, Any]],
    stats: dict[str, Any],
    warnings: list[str],
    files: list[str],
    suppliers: dict[str, str],
) -> JsonReport:
    """Собрать успешный ответ."""
    return {
        "ok": True,
        "version": REPORT_VERSION,
        "action": action,
        "positions": positions,
        "stats": stats,
        "warnings": warnings,
        "files": files,
        "suppliers": suppliers,
        "disabled_suppliers": {},
        "error": None,
    }


def error_payload(
    action: str,
    kind: str,
    message: str,
    *,
    compact: bool = False,
) -> Mapping[str, Any]:
    """Собрать ответ об ошибке. compact — только ok/action/error (не разбор)."""
    error: JsonError = {"kind": kind, "message": message}
    if compact:
        return {_OK_KEY: False, "action": action, "error": error}
    return {
        "ok": False,
        "version": REPORT_VERSION,
        "action": action,
        "positions": [],
        "stats": empty_stats(0),
        "warnings": [],
        "files": [],
        "suppliers": {},
        "disabled_suppliers": {},
        "error": error,
    }
