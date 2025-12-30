"""
tests common price parser
"""

from parsers.common_price_grouper import CommonPriceGrouper
from parsers.row_item.row_item import RowItem


def test_grouper() -> None:
    """
    ---- грузовая шина
    315/80R22.5 Кама NU 701 156/150K                      форточки
    315/80R22.5 КАМА NU701 156/150K TL НКШЗ               запаска
    315/80R22.5 НКШЗ КАМА-NU 701 Универсальная 156/150K   мим

    """
    item1 = RowItem(
        {
            "brand": "НКШЗ",
            "width": "315",
            "model": "NU701",
            "diameter": "22.5",
            "season": "Летняя",
            "article": "1430006",
            "code_art": "00000023103",
            "rest_count": 19,
            "price_purchase": "33631",
            "price_recommended": "34940",
            "height_percent": "80",
            "index_load": "156/150",
            "index_velocity": "K",
            "title": "315/80R22.5 КАМА NU701 156/150K TL НКШЗ",
            "type_production": "Грузовая шина",
            "manufacturer_name": "НКШЗ",
            "sup_name": "Запаска (шины)",
            "spike": "",
            "price_markup": 10,
            "order": 1,
        }
    )
    item2 = RowItem(
        {
            "code": 86240855887.0,
            "title": "315/80R22.5 НКШЗ КАМА-NU 701 Универсальная 156/150K",
            "manufacturer_name": "НКШЗ",
            "model": "КАМА-NU 701",
            "width": "315",
            "height_percent": "80",
            "construction_type": "R",
            "diameter": "22.5",
            "axis": "Ведущая",
            "intimacy": "",
            "layering": "",
            "index_load": "156/150",
            "index_velocity": "K",
            "rest_count": 6.0,
            "price_purchase": 33631.0,
            "price_recommended": 36320.0,
            "sup_name": "Мим",
            "spike": "",
            "season": "",
            "price_markup": 20,
            "type_production": "Грузовая шина",
            "order": 2,
        }
    )

    grouper = CommonPriceGrouper([item1, item2])
    print(grouper.get_double_items())
