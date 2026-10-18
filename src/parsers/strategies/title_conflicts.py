"""Расхождение колонки поставщика с названием: название главнее, расхождение — в лог."""

from __future__ import annotations

import logging
from typing import Any

from domain.row_item.row_item import RowItem
from infrastructure.logging.console import FILE_ONLY
from parsers.strategies._title_wins import DISK_TITLE_WINS, TIRE_TITLE_WINS

logger = logging.getLogger(__name__)

# Поля, где название главнее колонки поставщика.
TITLE_WINS_FIELDS = tuple(sorted(TIRE_TITLE_WINS | DISK_TITLE_WINS))


def _canon(raw: Any) -> str:
    """Значение для сравнения: 40, '40' и '40.0' — одно и то же."""
    text = str(raw).strip().upper()
    try:
        return str(float(text.replace(',', '.')))
    except ValueError:
        return text


def column_values(row_item: RowItem) -> dict[str, Any]:
    """Значения полей из колонок прайса до разбора названия."""
    return {key: row_item.get_field(key) for key in TITLE_WINS_FIELDS}


def log_title_conflicts(row_item: RowItem, from_columns: dict[str, Any], title: str | None) -> None:
    """Для полей, где название перебило колонку, записать «было → стало» (только в файл) и пометить позицию."""
    for key, column_value in from_columns.items():
        title_value = row_item.get_field(key)
        if column_value is None or _canon(column_value) == _canon(title_value):
            continue
        change = f'{key} {column_value!r} → {title_value!r}'
        row_item.set_field('title_conflict', True)
        logger.warning(
            f'Колонка поставщика расходится с названием: {change} (верим названию) // {title}',
            extra={FILE_ONLY: True},
        )


def title_conflicts_message(count: int) -> str:
    """Сводка по расхождениям колонок с названием; пустая строка — расхождений нет."""
    if not count:
        return ''
    return f'Колонки поставщика расходятся с названием (верим названию), позиций: {count}; подробности в логе'
