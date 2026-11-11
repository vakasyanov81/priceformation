"""Структурная проверка независимой схемы JSONL."""

import re
from pathlib import PurePosixPath
from typing import Any

from domain.product_groups import ProductGroup

META_VERSION = 2
IDENTITY_KEYS = ('template_id', 'product_group', 'schema_version')


def valid_name(name: str) -> bool:
    path = PurePosixPath(name)
    forbidden = (path.is_absolute(), '..' in path.parts, '\\' in name)
    if str(path) != name:
        return False
    return not any(forbidden) and path.suffix == '.jsonl'


def valid_schema(schema: object) -> bool:
    if not isinstance(schema, dict):
        return False
    required = {*IDENTITY_KEYS, 'columns', 'value_codes'}
    if set(schema) != required:
        return False
    checks = (
        isinstance(schema['template_id'], str),
        bool(schema['template_id']),
        schema['product_group'] in tuple(ProductGroup),
        positive_integer(schema['schema_version']),
        _valid_map(schema['columns'], r'[1-9]\d*'),
        _valid_map(schema['value_codes'], r'@[1-9]\d*'),
    )
    return all(checks)


def positive_integer(version: object) -> bool:
    return isinstance(version, int) and not isinstance(version, bool) and version > 0


def valid_envelope(payload: Any) -> bool:
    if not isinstance(payload, dict) or set(payload) != {'version', 'files'}:
        return False
    checks = (
        positive_integer(payload['version']),
        payload['version'] == META_VERSION,
        isinstance(payload['files'], dict),
    )
    return all(checks)


def _valid_map(mapping: object, pattern: str) -> bool:
    if not isinstance(mapping, dict):
        return False
    checks = (_valid_entry(key, label, pattern) for key, label in mapping.items())
    return all(checks)


def _valid_entry(key: str, label: object, pattern: str) -> bool:
    return re.fullmatch(pattern, key) is not None and isinstance(label, str)
