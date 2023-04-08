from core import log_msg
from database.nomenclature import insert_brand, insert_nomenclature
from database.supplier import get_suppliers, insert_supplier
from parsers.row_item.row_item import RowItem


async def save_nomenclature_to_db(common_price):
    """save to database"""
    sup_names = common_price.supplier_info()
    inserted_supplier_count = 0

    log_msg("-------- Обновление базы данных --------", need_print_log=True)
    if sup_names:
        inserted_supplier_count = await insert_supplier(sup_names)
    log_msg(f"Добавлено поставщиков: {inserted_supplier_count}", need_print_log=True)

    suppliers = await get_suppliers()
    suppliers = {sup.get("supplier_name"): sup.get("supplier_id") for sup in suppliers}
    inserted_brand_count = await insert_brand(get_brands(common_price.result)) or 0
    log_msg(f"Добавлено брэндов: {inserted_brand_count}", need_print_log=True)
    inserted_nomenclature_count = await insert_nomenclature(
        common_price.result, suppliers
    )
    log_msg(
        f"Добавлено номенклатуры: {inserted_nomenclature_count}", need_print_log=True
    )


def get_brands(nomenclatures: list[RowItem]) -> list:
    brands = set()
    for n in nomenclatures:
        if n.manufacturer:
            brands.add(n.manufacturer)
    return list(brands)
