"""Группы складов Форточек из настроек: разбор файла и проверка структуры."""

import json
import re
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from domain.config_context import get_config_provider
from domain.exceptions import ConfigValidationError
from domain.four_tochki import FourTochkiApiWarehouse, FourTochkiWarehouse, FourTochkiWarehouseGroup
from parsers.remote.four_tochki_warehouses import (
    WAREHOUSES_CONFIG_FILE,
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


def _payload(*groups: Any) -> dict[str, Any]:
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
    groups = {group.name: group for group in load_four_tochki_warehouse_groups(get_config_provider())}

    assert groups['novosibirsk'].merge is True
    assert 'НСБ' in groups['novosibirsk'].keywords
    assert groups['order'].delivery_period == 5


_WHERE = 'four_tochki_warehouses.json → groups[1]'


@pytest.mark.parametrize(
    ('entry', 'message'),
    [
        ({'name': 'g'}, f'{_WHERE}: отсутствует обязательный ключ «keywords»'),
        ({'name': 'g', 'keywords': 'Омск'}, f'{_WHERE} → keywords: ожидается список строк'),
        ({'name': 'g', 'keywords': [1]}, f'{_WHERE} → keywords: ожидается список строк'),
        ({'name': 'g', 'keywords': []}, f'{_WHERE} → keywords: ожидается непустой список'),
        ({'keywords': ['Омск']}, f'{_WHERE}: отсутствует обязательный ключ «name»'),
        ({'name': '  ', 'keywords': ['Омск']}, f'{_WHERE} → name: ожидается непустая строка'),
        ({'name': 'g', 'keywords': ['Омск'], 'merge': 'да'}, f'{_WHERE}: «merge» должно быть true/false'),
        ({'name': 'g', 'keywords': ['Омск'], 'available': 5}, f'{_WHERE} → available: ожидается строка'),
        ({'name': 'g', 'keywords': ['Омск'], 'delivery_period': 'x'}, f'{_WHERE} → delivery_period'),
    ],
)
def test_group_error_names_file_and_group_index(entry: dict[str, Any], message: str) -> None:
    """Ошибка в любом ключе группы называет файл и номер группы, а не только ключ."""
    with pytest.raises(ConfigValidationError, match=re.escape(message)):
        parse_warehouse_groups(_payload(_group_entry('first', 'Томск'), entry))


def test_group_that_is_not_object_names_file_and_index() -> None:
    """Группа не объект — в сообщении файл, номер группы и полученное значение."""
    with pytest.raises(ConfigValidationError, match=re.escape(f'{_WHERE}: ожидается объект группы, получено 5')):
        parse_warehouse_groups(_payload(_group_entry('first', 'Томск'), 5))


def test_structure_errors_name_file() -> None:
    """Ошибки корня и пустого списка называют файл."""
    with pytest.raises(
        ConfigValidationError, match=r'^four_tochki_warehouses\.json: ожидается объект с ключом «groups»'
    ):
        parse_warehouse_groups([])
    with pytest.raises(ConfigValidationError, match=r'^four_tochki_warehouses\.json → groups: список групп пуст$'):
        parse_warehouse_groups({'groups': []})
    with pytest.raises(ConfigValidationError, match=r'^four_tochki_warehouses\.json: группа «g» указана дважды$'):
        parse_warehouse_groups(_payload(_group_entry('g', 'a'), _group_entry('g', 'b')))


def test_load_reads_file_from_injected_provider(tmp_path: Path) -> None:
    """файл групп складов берётся у переданного провайдера, а не у глобального локатора"""
    config = tmp_path / 'groups.json'
    group = {'name': 'g', 'keywords': ['k'], 'merge': False}
    config.write_text(json.dumps({'groups': [group]}), encoding='utf-8')
    injected = MagicMock()
    injected.config_file.return_value = str(config)

    groups = load_four_tochki_warehouse_groups(injected)

    assert [group.name for group in groups] == ['g']
    injected.config_file.assert_called_once_with(WAREHOUSES_CONFIG_FILE)
