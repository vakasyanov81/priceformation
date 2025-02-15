"""nomenclature CRUD logic"""

import traceback
from enum import Enum
from sqlite3 import DatabaseError
from typing import Dict

from src.core import err_msg, log_msg
from src.database.db import fetch_all, fetch_as_dict, get_db
from src.parsers.common_price import CommonPrice
from src.parsers.row_item.row_item import RowItem
from .exception import DBError
from .supplier import get_statistic, get_suppliers, insert_supplier


class ProductState(Enum):
    """Состояние товара"""

    NEW_STATE: 1
    OLD_STATE: 0


async def insert_nomenclature(nomenclatures: list[RowItem], suppliers: dict):
    """insert nomenclature list to database"""
    nom_types = await fetch_as_dict(SQL_GET_NOMENCLATURE_TYPE)
    inserted_count = 0
    for _chunk in chunks(nomenclatures):
        try:
            res = await fetch_all(insert_nomenclature_sql(_chunk, suppliers, nom_types), autocommit=True)
            inserted_count += len(res)
        except DatabaseError as _exc:
            err_msg(str(_exc))
            err_msg(traceback.format_exc())
            await (await get_db()).rollback()
            await (await get_db()).close()
            raise DBError("Ошибка при вставке номенклатуры") from _exc
    return inserted_count


def insert_nomenclature_sql(nomenclatures: list[RowItem], suppliers: dict, nomenclature_type: Dict[str, int]) -> str:
    """prepare sql query for insert nomenclatures"""
    noms = []

    for nom in nomenclatures:
        row = [
            suppliers.get(nom.supplier_name),  # supplier_id
            nom.title.replace("'", r"''"),
            nom.code,
            nom.price_opt,
            nom.price_markup,
            nom.rest_count,
            nom.brand,
            nomenclature_type.get(nom.type_production),
        ]
        noms.append(",".join(prepare_to_insert(row)))
    data = ",".join([f"({nom})" for nom in noms])
    sql = SQL_INSERT_NOMENCLATURE.format(data_=data)
    return sql


def chunks(data: list, batch_size=200) -> list:
    """break into batch"""
    _chunks = []
    left_index = 0
    right_index = batch_size
    while True:
        if right_index >= len(data):
            right_index = len(data)
            _chunks.append(data[left_index:right_index])
            break
        _chunks.append(data[left_index:right_index])

        right_index += batch_size
        left_index += batch_size
    return _chunks


async def insert_brand(brand: list):
    """insert brand to database"""
    if not brand:
        return 0
    data = ",".join([f"('{b}')" for b in brand])
    sql = SQL_INSERT_BRAND.format(data_=data)
    res = await fetch_all(sql)
    return len(res)


def prepare_to_insert(data: list):
    """prepare data for insert"""
    return [f"'{d}'" if d else "NULL" for d in data]


async def save_nomenclature_to_db(common_price: CommonPrice):
    """save to database"""
    sup_names = common_price.supplier_info()
    supplier_count_before = (await get_statistic()).supplier_count

    log_msg("-------- Обновление базы данных --------", need_print_log=True)
    if sup_names:
        await insert_supplier(sup_names)
    supplier_count_after = (await get_statistic()).supplier_count
    log_msg(
        f"Добавлено поставщиков: {supplier_count_after - supplier_count_before}",
        need_print_log=True,
    )

    suppliers = await get_suppliers()
    suppliers = {sup.get("supplier_name"): sup.get("supplier_id") for sup in suppliers}
    inserted_brand_count = await insert_brand(get_brands(common_price.get_result())) or 0
    log_msg(f"Добавлено брэндов: {inserted_brand_count}", need_print_log=True)
    inserted_nomenclature_count = await insert_nomenclature(common_price.get_result(), suppliers)
    log_msg(f"Добавлено номенклатуры: {inserted_nomenclature_count}", need_print_log=True)


def get_brands(nomenclatures: list[RowItem]) -> list:
    """get list brand from nomenclature list"""
    brands = set()
    for nom in nomenclatures:
        if nom.manufacturer:
            brands.add(nom.manufacturer)
    return list(brands)


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
