"""JSON-отчёт разбора прайса для сторонних скриптов (Django и др.)."""

from __future__ import annotations

import json
import sys
from typing import Any, TextIO, TypedDict

REPORT_VERSION = 1


class JsonError(TypedDict):
    """Ошибка запуска."""

    kind: str
    message: str


class JsonReport(TypedDict):
    """Стабильная схема ответа CLI."""

    ok: bool
    version: int
    action: str
    took: str
    positions: list[dict[str, Any]]
    stats: dict[str, Any]
    warnings: list[str]
    files: list[str]
    suppliers: dict[str, str]
    error: JsonError | None


def dump_json(payload: JsonReport) -> str:
    """Сериализовать отчёт в одну JSON-строку."""
    return json.dumps(payload, ensure_ascii=False, default=str)


def emit_json(
    payload: JsonReport,
    stream: TextIO | None = None,
    *,
    elapsed: float | None = None,
) -> None:
    """Печать JSON в stdout (или переданный поток)."""
    if elapsed is not None:
        payload["took"] = f"{round(elapsed)} seconds"
    print(dump_json(payload), file=stream or sys.stdout, flush=True)


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
        "took": "0 seconds",
        "positions": positions,
        "stats": stats,
        "warnings": warnings,
        "files": files,
        "suppliers": suppliers,
        "error": None,
    }


def error_payload(action: str, kind: str, message: str) -> JsonReport:
    """Собрать ответ об ошибке (та же схема ключей)."""
    return {
        "ok": False,
        "version": REPORT_VERSION,
        "action": action,
        "took": "0 seconds",
        "positions": [],
        "stats": empty_stats(0),
        "warnings": [],
        "files": [],
        "suppliers": {},
        "error": {"kind": kind, "message": message},
    }
