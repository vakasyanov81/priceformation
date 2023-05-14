"""supplier database logic"""
from sqlite3 import DatabaseError
from typing import Dict, NamedTuple, Tuple

from core import err_msg
from database.db import fetch_all, fetch_as_dict, insert
from parsers.common_price import SupplierInfo

from .exception import DBError


async def get_suppliers():
    return await fetch_all(SQL_GET_ALL_SUPPLIER)


class DBStatistic(NamedTuple):
    supplier_count: int
    brand_count: int
    nomenclature_by_supllier_count: Dict[int, int]


async def get_statistic() -> DBStatistic:
    res = await fetch_as_dict(SQL_GET_STATISTIC)
    return DBStatistic(**res)


async def insert_supplier(sup_names: Dict[str, SupplierInfo]):
    try:
        res = await insert(*insert_supplier_sql(sup_names))
        return len(res)
    except DatabaseError as _exc:
        import traceback

        err_msg(str(_exc))
        err_msg(traceback.format_exc())
        raise DBError("Ошибка при вставке поставщиков") from _exc


def insert_supplier_sql(suppliers: Dict[str, SupplierInfo]) -> Tuple[str, list]:
    """Подготовка вставки данных по поставщикам"""
    # data = ",".join([f"({id_}, '{sup.name}')" for id_, sup in suppliers.items()])
    data = [(int(id_), sup.name) for id_, sup in suppliers.items()]
    sql = (
        "INSERT INTO supplier (supplier_id, supplier_name) "
        "VALUES (?, ?) ON CONFLICT DO NOTHING RETURNING rowid;"
    )

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
               'nomenclature_by_supllier_count',
               (SELECT * FROM NOM_STAT),
               'brand_count',
               (SELECT COUNT(*)
                FROM brand)
           )
"""
