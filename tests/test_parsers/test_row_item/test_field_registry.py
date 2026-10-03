"""Инварианты реестра плоских полей строки."""

import pytest

from parsers.row_item import field_registry as registry
from parsers.row_item import row_item_formatter as row_format
from parsers.row_item.field_registry import DUPLICATE, FIELD_KEYS, FIELD_SPECS, FieldSpec
from parsers.row_item.row_item import DEFAULT_VALUES, FIELD_FORMAT

_PRICE_KEYS = ('price_opt', 'price_recommended', 'price_markup')
_VO_GROUPS = (registry.IDENTITY, 'tire', 'disk', registry.PRICING, registry.STOCK, DUPLICATE, registry.VENDOR)


def _formatted_keys() -> set[str]:
    return {key for keys in FIELD_FORMAT.values() for key in keys}


def _defaulted_keys() -> set[str]:
    return {key for keys in DEFAULT_VALUES for key in keys}


def test_keys_are_unique() -> None:
    """плоский ключ встречается в реестре один раз."""
    assert len(FIELD_KEYS) == len(set(FIELD_KEYS))
    assert set(FIELD_KEYS) == set(registry.SPEC_BY_KEY)


def test_every_formatted_field_is_in_registry() -> None:
    """каждое поле с приведением из FIELD_FORMAT описано в реестре."""
    assert _formatted_keys() <= set(FIELD_KEYS)


def test_every_registry_field_has_a_coercer() -> None:
    """у каждого поля реестра есть приведение: text или formatter из FIELD_FORMAT."""
    allowed = {row_format.text, *(formatter for formatter in FIELD_FORMAT)}
    assert {spec.coercer for spec in FIELD_SPECS} <= allowed


def test_formatted_fields_use_same_coercer() -> None:
    """реестр и FIELD_FORMAT назначают одно и то же приведение."""
    formatters = {formatter: set(keys) for formatter, keys in FIELD_FORMAT.items()}
    for spec in FIELD_SPECS:
        if spec.key not in _formatted_keys():
            continue
        assert spec.coercer in formatters
        assert spec.key in formatters[spec.coercer]


def test_defaults_match_default_values() -> None:
    """дефолты реестра совпадают с DEFAULT_VALUES, у остальных полей дефолта нет."""
    for spec in FIELD_SPECS:
        expected = 0 if spec.key in _defaulted_keys() else None
        assert spec.default == expected, spec.key


def test_only_price_fields_have_default() -> None:
    """ненулевой дефолт есть только у цен — их читают без проверки на None."""
    with_default = [spec.key for spec in FIELD_SPECS if spec.default is not None]
    assert sorted(with_default) == sorted(_PRICE_KEYS)


@pytest.mark.parametrize(
    'path_prefix',
    _VO_GROUPS,
)
def test_paths_start_with_vo_group(path_prefix: str) -> None:
    """путь поля — это группа VO и имя атрибута в ней."""
    for spec in FIELD_SPECS:
        if spec.path.startswith(f'{path_prefix}.'):
            group, _, attribute = spec.path.partition('.')
            assert group == path_prefix
            assert attribute.isidentifier()


def test_spec_of_known_and_unknown_key() -> None:
    """spec_of отдаёт описание поля и None для вендорского ключа."""
    assert registry.spec_of('price_markup') == registry.SPEC_BY_KEY['price_markup']
    assert registry.spec_of('hash_title') is None


def test_spec_is_immutable() -> None:
    """описание поля нельзя переписать: key/path/coercer/default зафиксированы."""
    spec = registry.SPEC_BY_KEY['width']
    assert isinstance(spec, FieldSpec)
    with pytest.raises(AttributeError):
        spec.key = 'other'  # type: ignore[misc]
