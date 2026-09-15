"""Подготовка title — утилиты и константы.

Классы ParserTitleOps / ParserTitleFilters удалены (задача 4: composition over inheritance).
Логика перенесена в title_filter.py; классметоды — в base_parser.py.
"""

import re

from parsers.row_item.row_item import RowItem

_COMMA_IN_NUMBER = re.compile(r'(\d),(\d)')

_SPIKE_YES = {'ш.', 'да'}
_SEASON_TITLES = {'зима': 'Зимняя', 'лето': 'Летняя'}


def replace_season(row_item: RowItem) -> str | None:
    """Каноническое имя сезона или исходная строка."""
    if not row_item.season:
        return None
    return _SEASON_TITLES.get(row_item.season.lower()) or row_item.season
