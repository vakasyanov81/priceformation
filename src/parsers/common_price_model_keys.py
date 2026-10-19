"""Ключи группировки позиций с канонической моделью: модели с лишними словами склеены."""

from collections import defaultdict
from typing import Any

from domain.row_item.row_item import RowItem
from parsers.common_price_group_key import MODEL_KEY_INDEX, group_key
from parsers.common_price_model import model_tokens
from parsers.common_price_model_merge import ModelEntry, Tokens, merge_models

GroupKey = tuple[str, ...]
KeyedItem = tuple[GroupKey, RowItem]


def keys_with_merged_models(row_items: list[RowItem], aliases_map: dict[str, Any]) -> list[KeyedItem]:
    """Ключи группировки, где модели с лишними словами заменены канонической моделью ядра ключа."""
    keyed = [(group_key(row_item, aliases_map), row_item) for row_item in row_items]
    canonical = _canonical_by_core(keyed)
    return [_merged(keyed_row, canonical) for keyed_row in keyed]


def _canonical_by_core(keyed: list[KeyedItem]) -> dict[GroupKey, dict[str, str]]:
    """Для каждого ядра ключа — карта «ключ модели → канонический ключ модели»."""
    entries: dict[GroupKey, list[ModelEntry]] = defaultdict(list)
    for key, row_item in keyed:
        entries[_core_key(key)].append(_model_entry(key, row_item))
    return {core: merge_models(core_entries) for core, core_entries in entries.items()}


def _merged(keyed_row: KeyedItem, canonical: dict[GroupKey, dict[str, str]]) -> KeyedItem:
    key, row_item = keyed_row
    return _replace_model(key, canonical[_core_key(key)]), row_item


def _model_entry(key: GroupKey, row_item: RowItem) -> ModelEntry:
    return key[MODEL_KEY_INDEX], _tokens(row_item)


def _tokens(row_item: RowItem) -> Tokens:
    identity = row_item.identity
    return model_tokens(identity.model, identity.manufacturer, identity.brand)


def _core_key(key: GroupKey) -> GroupKey:
    """Ключ без модели: по нему модели сравниваются между собой."""
    return key[:MODEL_KEY_INDEX] + key[MODEL_KEY_INDEX + 1 :]


def _replace_model(key: GroupKey, canonical: dict[str, str]) -> GroupKey:
    """Подставить в ключ каноническую модель; модели без записи в карте остаются как есть."""
    parts = list(key)
    parts[MODEL_KEY_INDEX] = canonical.get(key[MODEL_KEY_INDEX], key[MODEL_KEY_INDEX])
    return tuple(parts)
