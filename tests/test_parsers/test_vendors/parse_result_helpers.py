"""Helpers for vendor parse-result fixtures in tests."""

from typing import Any, cast


def get_rows(parse_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all rows for the first price file in parse result."""
    price_file_path = next(iter(parse_result))
    return cast(list[dict[str, Any]], parse_result[price_file_path])


def get_first_row_item(parse_result: dict[str, Any]) -> dict[str, Any]:
    """Return the first row for the first price file in parse result."""
    return get_rows(parse_result)[0]
