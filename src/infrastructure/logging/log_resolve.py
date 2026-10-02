"""Текстовые подписи и цвета уровней логирования для форматтеров и фильтров."""

import logging

__level_map__ = {
    logging.ERROR: 'ERROR',
    logging.INFO: 'INFO',
    logging.WARNING: 'WARNING',
}
__level_colors__ = {'ERROR': 'red', 'WARNING': 'yellow'}


def get_log_level_text(log_level: int) -> str:
    """Map logging level int to text label."""
    return __level_map__.get(log_level) or 'INFO'


def get_level_color(level_text: str) -> str | None:
    """Цвет уровня для консоли; INFO и служебные записи остаются без цвета."""
    return __level_colors__.get(level_text)
