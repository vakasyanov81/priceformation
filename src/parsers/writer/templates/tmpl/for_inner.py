"""
write template for internal use
"""

from parsers.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import IWriteTemplate


class ForInner(IWriteTemplate):
    """write template for internal use"""

    __COLUMNS__ = [
        {
            "Тип товара": {
                "style": {"width": 256 * 10},
                "field": RowItem.type_production.name,
            }
        },
        {
            "Бренд": {
                "style": {"width": 356 * 15},
                "field": RowItem.manufacturer.name,
            }
        },
        {"Номенклатура": {"style": {"width": 256 * 100}, "field": RowItem.title.name}},
        {"Сезон": {"field": RowItem.season.name}},
        {"Шип": {"field": RowItem.spike.name}},
        {
            "Цена закуп.": {
                "style": {"width": 256 * 15},
                "field": RowItem.price_opt.name,
                "format": "@",
            }
        },
        {"Цена": {"field": RowItem.price_markup.name}},
        {
            "Рекомендуемая Цена": {
                "style": {"width": 256 * 25},
                "field": RowItem.price_recommended.name,
                "format": "@",
            }
        },
        {"Наценка %": {"style": {"width": 256 * 15}, "field": RowItem.percent_markup.name}},
        {"Остаток": {"field": RowItem.rest_count.name}},
        {
            "Поставщик": {
                "style": {"width": 256 * 15},
                "field": RowItem.supplier_name.name,
            }
        },
        {"Наличие": {"field": RowItem.available.name, "default_value": "В наличии"}},
        {"Срок доставки": {"field": RowItem.delivery_period.name}},
        {"Состояние": {"field": RowItem.condition.name, "default_value": "Новое"}},
        # {"Группа по параметрам": {"field": RowItem.__GROUP_BY_PARAMS__, "default_value": "1"}},
        # {
        #     "Дубль": {
        #         "field": RowItem.__IS_DOUBLE__,
        #     }
        # },
        # {
        #     "Главный дубль": {
        #         "field": RowItem.__DOUBLE_CANDIDATE__,
        #     }
        # },
    ]

    __COLOR__ = {
        "by_column": RowItem.supplier_name.name,
        "with_map": {
            "Пошк": "blue",
            "Мим": "#f7d5d2",
            "Запаска (остатки)": "#99706d",
            "Форточки": "#658c68",
        },
        "set_to_column_index": 0,
    }

    __FILE__ = "price_{now}.xlsx"

    __EXCLUDE__ = {}
