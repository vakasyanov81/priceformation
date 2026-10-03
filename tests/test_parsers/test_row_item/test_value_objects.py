"""Инварианты value objects: соответствие реестру полей и неизменяемость."""

import dataclasses
from types import NoneType
from typing import Any

import pytest

from parsers.row_item import field_registry as registry
from parsers.row_item.value_objects import (
    DiskParameters,
    DuplicateInfo,
    Pricing,
    ProductIdentity,
    Stock,
    TireDimensions,
    VendorMeta,
)

_VOS_BY_GROUP = (
    ('identity', ProductIdentity),
    ('tire', TireDimensions),
    ('disk', DiskParameters),
    ('pricing', Pricing),
    ('stock', Stock),
    ('duplicate', DuplicateInfo),
    ('vendor', VendorMeta),
)
_VOS = tuple(vo_type for _, vo_type in _VOS_BY_GROUP)
_GROUPS = tuple(group for group, _ in _VOS_BY_GROUP)
_POS_IDS = tuple(vo_type.__name__ for vo_type in _VOS)


def _group_of(vo_type: type) -> str:
    for group, mapped in _VOS_BY_GROUP:
        if mapped is vo_type:
            return group
    raise AssertionError(vo_type)


def _vo_names(vo_type: type) -> set[str]:
    return {entry.name for entry in dataclasses.fields(vo_type)}


def _registry_names(group: str) -> set[str]:
    prefix = f'{group}.'
    names = set()
    for spec in registry.FIELD_SPECS:
        if spec.path.startswith(prefix):
            names.add(spec.path[len(prefix) :])
    return names


def _field_names_with_types(vo_type: type) -> dict[str, Any]:
    return {entry.name: entry.type for entry in dataclasses.fields(vo_type)}


@pytest.mark.parametrize(('group', 'vo_type'), _VOS_BY_GROUP, ids=_POS_IDS)
def test_registry_covers_every_vo_field(group: str, vo_type: type) -> None:
    """каждое поле value object описано в реестре, и в реестре нет лишних полей."""
    assert _vo_names(vo_type) == _registry_names(group)


@pytest.mark.parametrize('vo_type', _VOS, ids=_POS_IDS)
def test_vo_is_frozen_with_slots(vo_type: type) -> None:
    """value object неизменяем и не имеет __dict__."""
    instance = vo_type()
    assert not hasattr(instance, '__dict__')
    first_field = dataclasses.fields(vo_type)[0].name
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(instance, first_field, 'x')


@pytest.mark.parametrize(('group', 'vo_type'), _VOS_BY_GROUP, ids=_POS_IDS)
def test_vo_default_matches_registry(group: str, vo_type: type) -> None:
    """дефолт поля совпадает с дефолтом реестра: цены нулевые, остальные None."""
    prefix = f'{group}.'
    empty = vo_type()
    for spec in registry.FIELD_SPECS:
        if spec.path.startswith(prefix):
            attribute = spec.path[len(prefix) :]
            assert getattr(empty, attribute) == spec.default, spec.key


def test_every_group_has_a_value_object() -> None:
    """каждая группа путей реестра — это value object."""
    groups_in_registry = {spec.path.split('.')[0] for spec in registry.FIELD_SPECS}
    assert groups_in_registry == set(_GROUPS)


def _declared_type(spec: registry.FieldSpec) -> tuple[type, ...]:
    group, attribute = spec.path.split('.')
    declared = _field_names_with_types(dict(_VOS_BY_GROUP)[group])[attribute]
    return declared if isinstance(declared, tuple) else (declared,)


@pytest.mark.parametrize('spec', registry.FIELD_SPECS, ids=registry.FIELD_KEYS)
def test_coercer_returns_declared_type(spec: registry.FieldSpec) -> None:
    """приведение из реестра даёт значение того типа, который объявлен в value object."""
    allowed = tuple(field for field in _declared_type(spec) if field is not NoneType)
    for raw in ('12', 12, 12.5):
        coerced = spec.coercer(raw)
        assert isinstance(coerced, allowed), (spec.key, raw, coerced)
