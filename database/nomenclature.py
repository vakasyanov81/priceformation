from dataclasses import dataclass
from decimal import Decimal as Money
from enum import Enum
from sqlite3 import DatabaseError
from typing import Dict

from core import err_msg
from database.db import fetch_all, fetch_as_dict
from parsers.row_item.row_item import RowItem

from .exception import DBError


class ProductState(Enum):
    """Состояние товара"""

    NEW_STATE: 1
    OLD_STATE: 0


@dataclass
class Nomenclature:
    supplier_id: int
    title: str
    code: str
    price: Money
    price_purchase: Money
    rest: int
    condition: ProductState
    brand: str
    nomenclature_type: str


async def insert_nomenclature(nomenclatures: list[RowItem], suppliers: dict):
    nom_types = await fetch_as_dict(SQL_GET_NOMENCLATURE_TYPE)
    inserted_count = 0
    for _chunk in chunks(nomenclatures):
        try:
            res = await fetch_all(insert_nomenclature_sql(_chunk, suppliers, nom_types))
            inserted_count += len(res)
        except DatabaseError as _exc:
            import traceback

            err_msg(str(_exc))
            err_msg(traceback.format_exc())
            raise DBError("Ошибка при вставке номенклатуры") from _exc
    return inserted_count


def insert_nomenclature_sql(
    nomenclatures: list[RowItem], suppliers: dict, nomenclature_type: Dict[str, int]
) -> str:
    noms = []

    for n in nomenclatures:
        row = [
            suppliers.get(n.supplier_name),  # supplier_id
            n.title.replace("'", r"''"),
            n.code,
            n.price_opt,
            n.price_markup,
            n.rest_count,
            n.brand,
            nomenclature_type.get(n.type_production),
        ]
        noms.append(",".join(prepare_to_insert(row)))
    data = ",".join([f"({nom})" for nom in noms])
    sql = SQL_INSERT_NOMENCLATURE.format(data_=data)
    return sql


def chunks(data: list, batch_size=200) -> list:
    _chunks = []
    left_index = 0
    right_index = batch_size
    while True:
        if right_index >= len(data):
            right_index = len(data)
            _chunks.append(data[left_index:right_index])
            break
        else:
            _chunks.append(data[left_index:right_index])

        right_index += batch_size
        left_index += batch_size
    return _chunks


async def insert_brand(brand: list):
    if not brand:
        return
    data = ",".join([f"('{b}')" for b in brand])
    sql = SQL_INSERT_BRAND.format(data_=data)
    res = await fetch_all(sql)
    return len(res)


def prepare_to_insert(data: list):
    """prepare data for insert"""
    return [f"'{d}'" if d else "NULL" for d in data]


SQL_INSERT_NOMENCLATURE = """
INSERT INTO nomenclature (supplier_id, title, code, price_purchase, price, rest, brand_id, nomenclature_type_id)
     VALUES {data_}
     ON CONFLICT(supplier_id, title, code) DO NOTHING RETURNING nomenclature_id;
"""

SQL_INSERT_BRAND = """
INSERT INTO brand (title)
    VALUES {data_}
    ON CONFLICT(title) DO NOTHING
    RETURNING brand_id
"""

SQL_GET_NOMENCLATURE_TYPE = """
SELECT json_group_array(json_object(
        title, type_id
    )) 
FROM nomenclature_type
"""
