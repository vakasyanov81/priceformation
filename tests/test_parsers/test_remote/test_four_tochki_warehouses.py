"""Группы складов Форточек из настроек: разбор файла и проверка структуры."""

from typing import Any

import pytest

from domain.exceptions import ConfigValidationError
from parsers.remote.four_tochki_warehouses import (
    FourTochkiApiWarehouse,
    FourTochkiWarehouse,
    FourTochkiWarehouseGroup,
    load_four_tochki_warehouse_groups,
    parse_warehouse_groups,
)

_NOVOSIBIRSK = FourTochkiWarehouseGroup(name='novosibirsk', keywords=('Новосибирск', 'НСБ'), merge=True)
_ORDER = FourTochkiWarehouseGroup(
    name='order',
    keywords=('Томск', 'Новокузнецк'),
    available='Под заказ',
    delivery_period=5,
)


def _payload(*groups: dict[str, Any]) -> dict[str, Any]:
    return {'groups': list(groups)}


def _group_entry(name: str, *keywords: str, **extra: Any) -> dict[str, Any]:
    """Группа из конфига: имя, ключевые слова и дополнительные поля."""
    return {'name': name, 'keywords': list(keywords), **extra}


def test_parse_groups_reads_all_settings() -> None:
    """Все поля группы доходят до объекта; необязательные без значения — по умолчанию."""
    groups = parse_warehouse_groups(
        _payload(
            {'name': 'novosibirsk', 'keywords': ['Новосибирск', ' НСБ '], 'merge': True},
            {'name': 'order', 'keywords': ['Томск', 'Новокузнецк'], 'available': 'Под заказ', 'delivery_period': 5},
        ),
    )

    assert groups == (_NOVOSIBIRSK, _ORDER)


def test_blank_available_becomes_none() -> None:
    """Пустая строка наличия — не задано; без merge склады не объединяются."""
    payload = _payload(_group_entry('g', 'Омск', available=''))
    group = parse_warehouse_groups(payload)[0]

    assert group.available is None
    assert group.merge is False
    assert group.delivery_period is None


@pytest.mark.parametrize('payload', [[], {}, {'groups': 'Новосибирск'}, {'warehouses': []}])
def test_root_without_groups_list_is_rejected(payload: Any) -> None:
    """Корень без списка групп — ошибка с именем файла."""
    with pytest.raises(ConfigValidationError, match=r'four_tochki_warehouses\.json: ожидается объект'):
        parse_warehouse_groups(payload)


def test_empty_groups_list_is_rejected() -> None:
    """Пустой список: выгружать было бы нечего."""
    with pytest.raises(ConfigValidationError, match='список групп пуст'):
        parse_warehouse_groups(_payload())


def test_group_must_be_object() -> None:
    """Группа — объект; путь до ошибки указывает индекс."""
    with pytest.raises(ConfigValidationError, match=r'groups\[0\]'):
        parse_warehouse_groups({'groups': ['Томск']})


def test_missing_name_is_rejected() -> None:
    """Без имени группу не вывести и не объединить: ошибка с путём до ключа."""
    with pytest.raises(ConfigValidationError, match='отсутствует обязательный ключ «name»'):
        parse_warehouse_groups(_payload({'keywords': ['Томск']}))


@pytest.mark.parametrize('keywords', [[], ['Томск', '  ']])
def test_empty_keywords_are_rejected(keywords: list[str]) -> None:
    """Пустое ключевое слово подошло бы под любой склад."""
    with pytest.raises(ConfigValidationError, match=r'groups\[0\] → keywords: ожидается непустой список'):
        parse_warehouse_groups(_payload({'name': 'g', 'keywords': keywords}))


def test_merge_must_be_flag() -> None:
    """merge — true/false."""
    with pytest.raises(ConfigValidationError, match='«merge» должно быть true/false'):
        parse_warehouse_groups(_payload({'name': 'g', 'keywords': ['Омск'], 'merge': 'да'}))


def test_duplicate_group_name_is_rejected() -> None:
    """Две группы с одним именем смешали бы склады при объединении."""
    payload = _payload(_group_entry('g', 'Томск'), _group_entry('g', 'Омск'))
    with pytest.raises(ConfigValidationError, match='группа «g» указана дважды'):
        parse_warehouse_groups(payload)


def test_group_applies_rules_to_api_warehouse() -> None:
    """Склад API получает имя группы, объединение и наличие со сроком."""
    tomsk = _ORDER.warehouse(FourTochkiApiWarehouse(id=1492, name='Томск'))

    novosibirsk = _NOVOSIBIRSK.warehouse(FourTochkiApiWarehouse(id=1, name='НСБ'))

    assert tomsk == FourTochkiWarehouse(
        id=1492,
        name='Томск',
        group='order',
        available='Под заказ',
        delivery_period=5,
    )
    assert novosibirsk.merge_group == 'novosibirsk'


@pytest.mark.usefixtures('example_vendors_provider')
def test_load_reads_config_file() -> None:
    """Файл берётся из папки конфигов провайдера; в эталонной копии — Новосибирск и склады под заказ."""
    groups = {group.name: group for group in load_four_tochki_warehouse_groups()}

    assert groups['novosibirsk'].merge is True
    assert 'НСБ' in groups['novosibirsk'].keywords
    assert groups['order'].delivery_period == 5
