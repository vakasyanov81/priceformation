"""Подбор складов Форточек из справочника API по ключевым словам групп и вывод на экран."""

import logging
from unittest.mock import patch

import pytest
from log_watch import LoggerWatcher

from domain.exceptions import CoreExceptionError
from parsers.remote.four_tochki_warehouse_selection import (
    FourTochkiNoWarehousesError,
    log_selected_warehouses,
    select_warehouses,
    warehouses_by_id,
)
from parsers.remote.four_tochki_warehouses import (
    FourTochkiApiWarehouse,
    FourTochkiWarehouse,
    FourTochkiWarehouseGroup,
)

_NOVOSIBIRSK = FourTochkiWarehouseGroup(name='novosibirsk', keywords=('Новосибирск', 'НСБ'), merge=True)
_ORDER = FourTochkiWarehouseGroup(
    name='order',
    keywords=('Томск', 'Новокузнецк'),
    available='Под заказ',
    delivery_period=5,
)
_API_WAREHOUSES = (
    FourTochkiApiWarehouse(id=1423, name='Новосибирск'),
    FourTochkiApiWarehouse(id=1254, name='ОХ г. нсб Бориса Богаткова'),
    FourTochkiApiWarehouse(id=276, name='ОХ Бердск Промышленная,1А/3'),
    FourTochkiApiWarehouse(id=1492, name='Томск'),
)


def test_select_matches_keywords_case_insensitive() -> None:
    """Склады подбираются по ключевым словам без учёта регистра; неподходящие не выгружаются."""
    warehouses = select_warehouses((_NOVOSIBIRSK, _ORDER), _API_WAREHOUSES)

    assert warehouses == (
        FourTochkiWarehouse(id=1423, name='Новосибирск', group='novosibirsk', merge_group='novosibirsk'),
        FourTochkiWarehouse(id=1254, name='ОХ г. нсб Бориса Богаткова', group='novosibirsk', merge_group='novosibirsk'),
        FourTochkiWarehouse(id=1492, name='Томск', group='order', available='Под заказ', delivery_period=5),
    )


def test_select_takes_first_matching_group() -> None:
    """Склад под ключевые слова двух групп относится к первой из них."""
    both = FourTochkiWarehouseGroup(name='all', keywords=('Томск',))

    warehouses = select_warehouses((both, _ORDER), (FourTochkiApiWarehouse(id=1492, name='Томск'),))

    assert [warehouse.group for warehouse in warehouses] == ['all']


def test_select_without_matches_raises() -> None:
    """Ни одного подходящего склада — выгружать нечего."""
    with (
        patch.object(CoreExceptionError, 'to_log'),
        pytest.raises(FourTochkiNoWarehousesError, match='нет ни одного'),
    ):
        select_warehouses((_ORDER,), (FourTochkiApiWarehouse(id=1, name='Омск'),))


def test_log_selected_warehouses_by_groups(watch_logger: LoggerWatcher) -> None:
    """На экран — склады по группам с правилами группы; пустая группа — предупреждение."""
    empty = FourTochkiWarehouseGroup(name='omsk', keywords=('Омск', 'Тара'))
    groups = (_NOVOSIBIRSK, _ORDER, empty)
    warehouses = select_warehouses(groups, _API_WAREHOUSES)

    entries = watch_logger('parsers.remote.four_tochki_warehouse_selection', logging.INFO)
    log_selected_warehouses(groups, warehouses)

    assert entries() == [
        (logging.INFO, 'Склады Форточек для выгрузки: 3'),
        (logging.INFO, 'Группа «novosibirsk» (объединяются в прайсе дрома): 2'),
        (logging.INFO, '  1423 — Новосибирск'),
        (logging.INFO, '  1254 — ОХ г. нсб Бориса Богаткова'),
        (logging.INFO, 'Группа «order» (без объединения, Под заказ, срок 5 дн.): 1'),
        (logging.INFO, '  1492 — Томск'),
        (logging.WARNING, 'Группа «omsk»: нет складов с ключевыми словами Омск, Тара'),
    ]


def test_warehouses_by_id_maps_api_ids() -> None:
    """Поиск по ID из API."""
    warehouse = FourTochkiWarehouse(id=7, name='Томск')

    assert warehouses_by_id((warehouse,)) == {7: warehouse}


def test_log_empty_group_does_not_stop_following_groups(watch_logger: LoggerWatcher) -> None:
    """Пустая группа в начале списка не обрывает вывод остальных групп."""
    empty = FourTochkiWarehouseGroup(name='omsk', keywords=('Омск',))
    warehouses = select_warehouses((_ORDER,), _API_WAREHOUSES)

    entries = watch_logger('parsers.remote.four_tochki_warehouse_selection', logging.INFO)
    log_selected_warehouses((empty, _ORDER), warehouses)

    assert entries() == [
        (logging.INFO, 'Склады Форточек для выгрузки: 1'),
        (logging.WARNING, 'Группа «omsk»: нет складов с ключевыми словами Омск'),
        (logging.INFO, 'Группа «order» (без объединения, Под заказ, срок 5 дн.): 1'),
        (logging.INFO, '  1492 — Томск'),
    ]
