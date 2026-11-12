"""Схема машинного ответа разбора v2."""

from typing import Any, TypedDict


class JsonError(TypedDict):
    """Ошибка запуска."""

    kind: str
    message: str


class JsonGroup(TypedDict):
    """Позиции и статистика одной модели."""

    positions: list[dict[str, Any]]
    stats: dict[str, Any]


class JsonReport(TypedDict):
    """Стабильная схема ответа CLI."""

    ok: bool
    version: int
    action: str
    groups: dict[str, JsonGroup]
    stats: dict[str, Any]
    warnings: list[str]
    files: list[str]
    suppliers: dict[str, str]
    disabled_suppliers: dict[str, str]
    error: JsonError | None
