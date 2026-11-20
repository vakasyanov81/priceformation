"""Утилиты строки позиции: признак шипов и канонический сезон."""

from domain.row_item.row_item import RowItem
from parsers.strategies.normalize import normalize_text, replace_homoglyphs
from parsers.vendor_config.slot_configs import ModelSeasonRules

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


def replace_season(row_item: RowItem, rules: ModelSeasonRules) -> str | None:
    """Нормализовать сезон поставщика или заполнить пропуск по модели."""
    season = row_item.tire.season
    if season:
        return _SEASON_TITLES.get(season.lower(), season)
    return _model_season(row_item.identity.title, rules) or _model_season(row_item.vendor.source_title, rules)


def _model_season(raw_title: str | None, rules: ModelSeasonRules) -> str | None:
    if not rules:
        return None
    title = replace_homoglyphs(normalize_text(raw_title))
    return next((season for pattern, season in rules if pattern.search(title)), None)
