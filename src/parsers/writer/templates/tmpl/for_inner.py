"""
write template for internal use
"""

from typing import Any, ClassVar

from domain.row_item.row_item import RowItem
from parsers.writer.templates.iwrite_template import IWriteTemplate, WriteColors, WriteColumns, WriteExclude

MAIN_DOUBLE_COLOR = '#ccffcc'
DOUBTFUL_COLOR = '#ff9999'

# Сомнительный дубль (цена отклоняется от главного на 5%+) — красным, главный дубль — светло-зелёным;
# красим всю строку, красный проверяется раньше зелёного.
DOUBLES_COLOR_RULES: list[dict[str, Any]] = [
    {'by_column': RowItem.doubtful_price.name, 'with_map': {True: DOUBTFUL_COLOR}, 'set_to_column_index': None},
    {'by_column': RowItem.double_candidate.name, 'with_map': {True: MAIN_DOUBLE_COLOR}, 'set_to_column_index': None},
]
DOUBLES_LEGEND: list[tuple[str, str]] = [
    (MAIN_DOUBLE_COLOR, 'Главный дубль группы'),
    (DOUBTFUL_COLOR, 'Сомнительный дубль: цена отклоняется от главного на 5% и более'),
]


class ForInner(IWriteTemplate):
    """write template for internal use"""

    template_id = 'for_inner'

    __COLUMNS__: ClassVar[WriteColumns] = [
        {
            'Тип товара': {
                'style': {'width': 256 * 10},
                'field': RowItem.type_production.name,
                'suffix': '*',
                'suffix_when': RowItem.type_corrected.name,
            }
        },
        {
            'Бренд': {
                'style': {'width': 356 * 15},
                'field': RowItem.manufacturer.name,
            }
        },
        {'Номенклатура': {'style': {'width': 256 * 100}, 'field': RowItem.title.name}},
        {'Сезон': {'field': RowItem.season.name}},
        {'Шип': {'field': RowItem.spike.name}},
        {
            'Цена закуп.': {
                'style': {'width': 256 * 15},
                'field': RowItem.price_opt.name,
                'format': '@',
            }
        },
        {'Цена': {'field': RowItem.price_markup.name}},
        {
            'Рекомендуемая Цена': {
                'style': {'width': 256 * 25},
                'field': RowItem.price_recommended.name,
                'format': '@',
            }
        },
        {'Наценка %': {'style': {'width': 256 * 15}, 'field': RowItem.percent_markup.name}},
        {'Наценка руб.': {'style': {'width': 256 * 15}, 'field': RowItem.absolute_markup.name}},
        {'Остаток': {'field': RowItem.rest_count.name}},
        {
            'Поставщик': {
                'style': {'width': 256 * 15},
                'field': RowItem.supplier_name.name,
            }
        },
        {
            'Склад': {
                'style': {'width': 256 * 25},
                'field': RowItem.warehouse_name.name,
            }
        },
        {'Наличие': {'field': RowItem.available.name, 'default_value': 'В наличии'}},
        {'Срок доставки': {'field': RowItem.delivery_period.name}},
        {'Состояние': {'field': RowItem.condition.name, 'default_value': 'Новое'}},
        {'Уценка': {'field': RowItem.marked_down.name, 'true_value': 'Да'}},
        {'Завод': {'field': RowItem.production_plant.name}},
        {'Год выпуска': {'field': RowItem.production_year.name}},
    ]

    # первая ячейка — цвет поставщика, остальные ячейки строки — подсветка дублей;
    # легенды нет: строки над шапкой общего прайса сломали бы его разбор у потребителей
    __COLOR__: ClassVar[WriteColors] = {
        'rules': [
            {
                'by_column': RowItem.supplier_name.name,
                'with_map': {
                    'Пошк': '#d9e2f3',
                    'Мим': '#f7d5d2',
                    'Запаска (остатки)': '#99706d',
                    'Форточки': '#658c68',
                },
                'set_to_column_index': 0,
            },
            *DOUBLES_COLOR_RULES,
        ],
    }

    __FILE__ = 'price_{now}.xlsx'

    __EXCLUDE__: ClassVar[WriteExclude] = {}
