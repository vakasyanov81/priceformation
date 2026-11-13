"""Полный аккумуляторный прайс: отдельные предложения и их характеристики."""

from typing import ClassVar

from domain.product_groups import ProductGroup
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput
from parsers.writer.templates.iwrite_template import IWriteTemplate, WriteColumns


class ForBatteries(IWriteTemplate):
    """Полный прайс аккумуляторов, доступный в CLI и штатной групповой записи."""

    template_id = 'for_batteries'
    __FILE__ = 'price_batteries_{now}.xlsx'
    __COLUMNS__: ClassVar[WriteColumns] = [
        {'Название': {'field': 'title', 'format': '@'}},
        {'Производитель': {'field': 'manufacturer_name', 'format': '@'}},
        {'Полярность': {'field': 'polarity', 'format': '@'}},
        {'Емкость': {'field': 'capacity_ah', 'format': '@'}},
        {'Пусковой ток': {'field': 'starting_current_a', 'format': '@'}},
        {'Длина': {'field': 'length_mm', 'format': '@'}},
        {'Ширина': {'field': 'width_mm', 'format': '@'}},
        {'Высота': {'field': 'height_mm', 'format': '@'}},
        {'Типоразмер': {'field': 'size_type', 'format': '@'}},
        {'Остаток': {'field': 'rest_count', 'format': '@'}},
        {'Закупочная цена': {'field': 'price_opt', 'format': '@'}},
        {'РРЦ': {'field': 'price_recommended', 'format': '@'}},
        {'Цена продажи': {'field': 'sale_price', 'format': '@'}},
        {'Наценка в руб': {'field': 'absolute_markup', 'format': '@'}},
        {'Наценка в %': {'field': 'percent_markup', 'format': '@'}},
        {'Клеммы': {'field': 'terminal_type', 'format': '@'}},
        {'EFB': {'field': 'efb', 'format': '@'}},
        {'AGM': {'field': 'agm', 'format': '@'}},
        {'Крепление': {'field': 'bottom_mount', 'format': '@'}},
        {'Обслуживаемость': {'field': 'serviceable', 'format': '@'}},
        {'Вес': {'field': 'weight', 'format': '@'}},
        {'Гарантия': {'field': 'warranty_months', 'format': '@'}},
        {'Поставщик': {'field': 'supplier_name', 'format': '@'}},
        {'Ценовая группа': {'field': 'price_group', 'format': '@'}},
    ]

    def output_spec(self) -> TemplateOutput:
        group = GroupOutput(
            ProductGroup.BATTERIES,
            'Аккумуляторы',
            self.columns(),
            {},
            {},
            file_name=self.get_file_name(),
        )
        return TemplateOutput(self.template_id, OutputMode.SEPARATE_FILES, (group,))
