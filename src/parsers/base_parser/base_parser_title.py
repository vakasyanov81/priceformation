"""Утилиты строки позиции: признак шипов и канонический сезон."""

from domain.row_item.row_item import RowItem

# Значения признака шипов, считающиеся «Да».
_SPIKE_YES = {'ш.', 'да'}
_SEASON_TITLES = {'зима': 'Зимняя', 'лето': 'Летняя'}


def get_spike_title(row_item: RowItem) -> str:
    """«Да», если у шины заданы шипы; иначе пустая строка."""
    if not row_item.tire.spike:
        return ''
    if row_item.tire.spike.strip().lower() in _SPIKE_YES:
        return 'Да'
    return ''


def replace_season(row_item: RowItem) -> str | None:
    """Каноническое имя сезона или исходная строка."""
    if not row_item.tire.season:
        return None
    return _SEASON_TITLES.get(row_item.tire.season.lower()) or row_item.tire.season
