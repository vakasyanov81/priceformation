"""supplier database logic"""

import traceback
from sqlite3 import DatabaseError
from typing import Dict, NamedTuple, Tuple

from src.core import err_msg
from src.database.db import fetch_all, fetch_as_dict, insert
from src.parsers.common_price import SupplierCode, SupplierName
from .exception import DBError


async def get_suppliers():
    """fetch all suppliers"""
    return await fetch_all(SQL_GET_ALL_SUPPLIER)


# pylint: disable=too-many-class-parents
class DBStatistic(NamedTuple):
    """database statist"""

    supplier_count: int
    brand_count: int
    nomenclature_by_supplier_count: Dict[int, int]


async def get_statistic() -> DBStatistic:
    """get database statistic"""
    res = await fetch_as_dict(SQL_GET_STATISTIC)
    return DBStatistic(**res)


async def insert_supplier(sup_names: Dict[SupplierCode, SupplierName]):
    """insert supplier"""
    try:
        res = await insert(*insert_supplier_sql(sup_names))
        return len(res)
    except DatabaseError as _exc:
        err_msg(str(_exc))
        err_msg(traceback.format_exc())
        raise DBError("Ошибка при вставке поставщиков") from _exc


def insert_supplier_sql(suppliers: Dict[SupplierCode, SupplierName]) -> Tuple[str, list]:
    """Подготовка вставки данных по поставщикам"""
    # data = ",".join([f"({id_}, '{sup.name}')" for id_, sup in suppliers.items()])
    data = [(int(id_), sup_name) for id_, sup_name in suppliers.items()]
    sql = """
         INSERT INTO supplier (supplier_id, supplier_name)
         VALUES (?, ?) ON CONFLICT DO NOTHING RETURNING supplier_id
    """

    return sql, data


SQL_GET_ALL_SUPPLIER = "SELECT * FROM supplier"

SQL_GET_STATISTIC = """
WITH NOM_STAT AS (
    SELECT json_group_object(
        CAST(supplier_id AS TEXT), cnt
    )
    FROM (SELECT supplier_id, count(*) cnt
          FROM nomenclature
          GROUP BY supplier_id) it
)
SELECT json_object(
               'supplier_count',
               (SELECT COUNT(*)
                FROM supplier),
               'nomenclature_by_supplier_count',
               (SELECT * FROM NOM_STAT),
               'brand_count',
               (SELECT COUNT(*)
                FROM brand)
           )
"""
