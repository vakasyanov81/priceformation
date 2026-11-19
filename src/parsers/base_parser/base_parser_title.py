"""Утилиты строки позиции: признак шипов и канонический сезон."""

import re

from domain.row_item.row_item import RowItem
from parsers.strategies.normalize import normalize_text, replace_homoglyphs
from parsers.strategies.product_types import ROCKBUSTER_H989

# Значения признака шипов, считающиеся «Да».
_SPIKE_YES = {'ш.', 'да'}
_SEASON_TITLES = {'зима': 'Зимняя', 'лето': 'Летняя'}
_ALL_SEASON_MODELS = re.compile(r'\b(?:greenstone st896|triangle (?:tr646|tr558|tr668a?))\b')
_WINTER_MODELS = re.compile(r'\btriangle (?:trd99\b|(?:snowlink )?trin\b.*\bll01\b|ll01\b)')


def get_spike_title(row_item: RowItem) -> str:
    """«Да», если у шины заданы шипы; иначе пустая строка."""
    if not row_item.tire.spike:
        return ''
    if row_item.tire.spike.strip().lower() in _SPIKE_YES:
        return 'Да'
    return ''


def replace_season(row_item: RowItem) -> str | None:
    """Определить сезон известной модели или нормализовать значение поставщика."""
    model_season = _model_season(row_item.identity.title) or _model_season(row_item.vendor.source_title)
    if model_season:
        return model_season
    season = row_item.tire.season
    return _SEASON_TITLES.get(season.lower(), season) if season else None


def _model_season(raw_title: str | None) -> str | None:
    title = replace_homoglyphs(normalize_text(raw_title))
    if _WINTER_MODELS.search(title):
        return 'Зимняя'
    if _ALL_SEASON_MODELS.search(title) or ROCKBUSTER_H989.search(title):
        return 'Всесезонная'
    return None
