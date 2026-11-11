"""Контракт стабильных идентификаторов товарных групп."""

import json

import pytest

from domain.product_groups import DuplicateGroupKey, ProductGroup


def test_known_groups_and_display_names() -> None:
    """Закрытый набор групп и названия соответствуют контракту конфигурации."""
    assert {group.value: group.display_name for group in ProductGroup} == {
        'tire_and_disk': 'шины + диски',
        'batteries': 'аккумуляторы',
    }


@pytest.mark.parametrize('identifier', ['tire_and_disk', 'batteries'])
def test_group_identifier_round_trip(identifier: str) -> None:
    """Во внешнем JSON сохраняется стабильный ключ, независимо от отображаемого названия."""
    group = ProductGroup(identifier)

    assert str(group) == identifier
    assert json.loads(json.dumps(group)) == identifier


@pytest.mark.parametrize(
    'identifier',
    ['', 'unknown', 'Tire_And_Disk', ' tire_and_disk', 'batteries ', 'шины + диски', 'аккумуляторы', 'Легковая'],
)
def test_group_rejects_noncanonical_identifier(identifier: str) -> None:
    """Название, категория, неизвестный ключ, регистр и пробелы не преобразуются в группу."""
    with pytest.raises(ValueError):
        ProductGroup(identifier)


def test_duplicate_group_key_scopes_local_id_to_product_group() -> None:
    """Одинаковые локальные номера разных товарных групп адресуют разные группы дублей."""
    tires = DuplicateGroupKey(ProductGroup.TIRE_AND_DISK, 7)
    batteries = DuplicateGroupKey(ProductGroup.BATTERIES, 7)

    assert tires != batteries
    assert tires.local_group_id == batteries.local_group_id
