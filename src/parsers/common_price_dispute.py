"""Явный конфликт шипа и сезона в группе дублей."""

from typing import Any, Iterable

from parsers.row_item.row_item import RowItem


def dispute_note(row_items: list[RowItem]) -> str:
    """Метки конфликта: шип и/или сезон."""
    notes = (
        _conflict_label("шип", (_spike_label(row_item.spike) for row_item in row_items)),
        _conflict_label("сезон", (_season_label(row_item.season) for row_item in row_items)),
    )
    return ", ".join(marker for marker in notes if marker)


def _conflict_label(field_label: str, canon_values: Iterable[str]) -> str:
    filled = {canon for canon in canon_values if canon}
    return field_label if len(filled) > 1 else ""


def _spike_label(raw: Any) -> str:
    text = str(raw or "").strip().lower()
    if text in {"да", "yes", "ш."}:
        return "да"
    if text in {"нет", "no"}:
        return "нет"
    return ""


def _season_label(raw: Any) -> str:
    text = str(raw or "").strip().lower()
    if text in {"зима", "зимняя"}:
        return "зимняя"
    if text in {"лето", "летняя"}:
        return "летняя"
    return text
