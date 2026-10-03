"""Инварианты реестра плоских полей строки."""

import dataclasses
from typing import get_type_hints

import pytest

from parsers.row_item import field_registry as registry
from parsers.row_item import row_item_formatter as row_format
from parsers.row_item.row_item import RowItem

_PRICE_KEYS = ('price_opt', 'price_recommended', 'price_markup')
_VO_GROUPS = (
    registry.IDENTITY,
    registry.TIRE,
    registry.DISK,
    registry.PRICING,
    registry.STOCK,
    registry.DUPLICATE,
    registry.VENDOR,
)
_TYPED_COERCERS = {
    row_format.code,
    row_format.money,
    row_format.floated,
    row_format.integer,
    row_format.int_or_float,
    row_format.boolean,
}
_ALL_COERCERS = _TYPED_COERCERS | {row_format.text}


def test_keys_are_unique() -> None:
    """плоский ключ встречается в реестре один раз."""
    assert len(registry.FIELD_KEYS) == len(set(registry.FIELD_KEYS))
    assert set(registry.FIELD_KEYS) == set(registry.SPEC_BY_KEY)


def test_every_field_has_known_coercer() -> None:
    """приведение каждого поля — одно из шести, и все шесть используются."""
    used = {spec.coercer for spec in registry.FIELD_SPECS}
    assert used <= _ALL_COERCERS
    assert used == _ALL_COERCERS


def test_only_price_fields_have_default() -> None:
    """ненулевой дефолт есть только у цен — их читают без проверки на None."""
    with_default = {spec.key: spec.default for spec in registry.FIELD_SPECS if spec.default is not None}
    assert with_default == dict.fromkeys(_PRICE_KEYS, 0)


def test_typed_fields_get_numeric_coercer() -> None:
    """числовые приведения стоят только у числовых по смыслу полей."""
    for spec in registry.FIELD_SPECS:
        if spec.coercer is row_format.text:
            continue
        assert spec.coercer in _TYPED_COERCERS, spec.key


@pytest.mark.parametrize('path_prefix', _VO_GROUPS)
def test_paths_start_with_vo_group(path_prefix: str) -> None:
    """путь поля — это группа VO и имя атрибута в ней."""
    for spec in registry.FIELD_SPECS:
        if spec.path.startswith(f'{path_prefix}.'):
            assert spec.group == path_prefix
            assert spec.attribute.isidentifier()


def test_spec_path_matches_group_and_attribute() -> None:
    """path — склейка группы и атрибута, а не отдельное поле реестра."""
    for spec in registry.FIELD_SPECS:
        assert spec.path == f'{spec.group}.{spec.attribute}'


def test_every_spec_points_to_existing_vo_field() -> None:
    """у каждого описания есть настоящее поле в value object его группы."""
    vo_classes = get_type_hints(RowItem)

    for spec in registry.FIELD_SPECS:
        vo = vo_classes[spec.group]
        assert spec.attribute in {vo_field.name for vo_field in dataclasses.fields(vo)}, spec.key


def test_registry_describes_every_vo_field() -> None:
    """каждое поле value object описано в реестре — иначе оно не попадёт в to_dict."""
    described = {(spec.group, spec.attribute) for spec in registry.FIELD_SPECS}

    vo_classes = get_type_hints(RowItem)

    for entry in dataclasses.fields(RowItem):
        if entry.name in {'extra', '_errors', '_set_keys'}:
            continue
        vo_fields = {vo_field.name for vo_field in dataclasses.fields(vo_classes[entry.name])}
        assert described & {(entry.name, name) for name in vo_fields} == {
            (entry.name, name) for name in vo_fields
        }, entry.name


def test_spec_of_known_and_unknown_key() -> None:
    """spec_of отдаёт описание поля и None для вендорского ключа."""
    assert registry.spec_of('price_markup') == registry.SPEC_BY_KEY['price_markup']
    assert registry.spec_of('hash_title') is None


def test_spec_is_immutable() -> None:
    """описание поля нельзя переписать: key/group/attribute зафиксированы."""
    spec = registry.SPEC_BY_KEY['width']
    with pytest.raises(AttributeError):
        spec.key = 'other'  # type: ignore[misc]


@pytest.mark.parametrize('key', registry.FIELD_KEYS, ids=registry.FIELD_KEYS)
def test_registry_field_lands_in_to_dict(key: str) -> None:
    """запись любого поля реестра попадает в плоский словарь строки."""
    assert key in RowItem({key: '12'}).to_dict()


def test_to_dict_has_no_keys_outside_registry() -> None:
    """в плоский словарь попадают только ключи реестра и вендорские pass-through."""
    row = RowItem({'title': 't1', 'hash_title': 'deadbeef'})
    assert set(row.to_dict()) == {'title', 'hash_title'}
