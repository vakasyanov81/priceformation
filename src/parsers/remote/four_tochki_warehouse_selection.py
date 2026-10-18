"""Подбор складов Форточек из справочника API по группам настроек и вывод их на экран."""

import logging
from collections.abc import Mapping, Sequence

from domain.exceptions import CoreExceptionError
from parsers.remote.four_tochki_warehouses import (
    WAREHOUSES_CONFIG_FILE,
    FourTochkiApiWarehouse,
    FourTochkiWarehouse,
    FourTochkiWarehouseGroup,
)

logger = logging.getLogger(__name__)


class FourTochkiNoWarehousesError(CoreExceptionError):
    """По ключевым словам групп не найден ни один склад API."""

    __MESSAGE__ = (
        'Среди складов API Форточек нет ни одного, подходящего под ключевые слова групп '
        f'из {WAREHOUSES_CONFIG_FILE}. Проверьте ключевые слова.'
    )


def select_warehouses(
    groups: Sequence[FourTochkiWarehouseGroup],
    api_warehouses: Sequence[FourTochkiApiWarehouse],
) -> tuple[FourTochkiWarehouse, ...]:
    """Склады API, подходящие под группы; склад попадает в первую подходящую группу.

    Склад, не подходящий ни под одну группу, не выгружается. Ни одного склада — ошибка:
    выгружать нечего.
    """
    selected: list[FourTochkiWarehouse] = []
    for api_warehouse in api_warehouses:
        group = next((group for group in groups if group.matches(api_warehouse.name)), None)
        if group is not None:
            selected.append(group.warehouse(api_warehouse))
    if not selected:
        raise FourTochkiNoWarehousesError()
    return tuple(selected)


def log_selected_warehouses(
    groups: Sequence[FourTochkiWarehouseGroup],
    warehouses: Sequence[FourTochkiWarehouse],
) -> None:
    """Вывести склады, по которым идёт выгрузка, по группам; группа без складов — предупреждение."""
    logger.info(f'Склады Форточек для выгрузки: {len(warehouses)}')
    for group in groups:
        members = [warehouse for warehouse in warehouses if warehouse.group == group.name]
        if not members:
            keywords = ', '.join(group.keywords)
            logger.warning(f'Группа «{group.name}»: нет складов с ключевыми словами {keywords}')
            continue
        details = group.describe()
        logger.info(f'Группа «{group.name}» ({details}): {len(members)}')
        for warehouse in members:
            logger.info(f'  {warehouse.id} — {warehouse.name}')


def warehouses_by_id(warehouses: Sequence[FourTochkiWarehouse]) -> Mapping[int, FourTochkiWarehouse]:
    """Склады по ID из API."""
    return {warehouse.id: warehouse for warehouse in warehouses}
