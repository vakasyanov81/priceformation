"""Полный аккумуляторный прайс: отдельные предложения и их характеристики."""

from typing import ClassVar

from domain.product_groups import ProductGroup
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput
from parsers.writer.templates.iwrite_template import IWriteTemplate, WriteColumns


class ForBatteries(IWriteTemplate):
    """Шаблон подключается к CLI после сквозной проверки двух групп."""

    template_id = 'for_batteries'
    __FILE__ = 'price_batteries_{now}.xlsx'
    __COLUMNS__: ClassVar[WriteColumns] = [
        {'Название': {'field': 'title', 'format': '@'}},
        {'Производитель': {'field': 'manufacturer_name', 'format': '@'}},
        {'Линейка': {'field': 'model', 'format': '@'}},
        {'Код': {'field': 'code', 'format': '@'}},
        {'Артикул интернет-магазина': {'field': 'code_art', 'format': '@'}},
        {'Артикул': {'field': 'code_man', 'format': '@'}},
        {'Ёмкость, А·ч': {'field': 'capacity_ah', 'format': '@'}},
        {'Пусковой ток, А': {'field': 'starting_current_a', 'format': '@'}},
        {'Стандарт тока': {'field': 'current_standard', 'format': '@'}},
        {'Клеммы': {'field': 'terminal_type', 'format': '@'}},
        {'Полярность': {'field': 'polarity', 'format': '@'}},
        {'EFB': {'field': 'efb', 'format': '@'}},
        {'AGM': {'field': 'agm', 'format': '@'}},
        {'Длина, мм': {'field': 'length_mm', 'format': '@'}},
        {'Ширина, мм': {'field': 'width_mm', 'format': '@'}},
        {'Высота, мм': {'field': 'height_mm', 'format': '@'}},
        {'Типоразмер': {'field': 'size_type', 'format': '@'}},
        {'Крепление': {'field': 'bottom_mount', 'format': '@'}},
        {'Обслуживаемость': {'field': 'serviceable', 'format': '@'}},
        {'Вес': {'field': 'weight', 'format': '@'}},
        {'Закупочная цена': {'field': 'price_opt', 'format': '@'}},
        {'РРЦ': {'field': 'price_recommended', 'format': '@'}},
        {'Цена продажи': {'field': 'sale_price', 'format': '@'}},
        {'Остаток': {'field': 'rest_count', 'format': '@'}},
        {'Гарантия, мес.': {'field': 'warranty_months', 'format': '@'}},
        {'Поставщик': {'field': 'supplier_name', 'format': '@'}},
        {'Ценовая группа': {'field': 'price_group', 'format': '@'}},
        {'Сертификат': {'field': 'certificate_url', 'format': '@'}},
        {'Группа дублей': {'field': 'group_id', 'format': '@'}},
        {'Главное предложение': {'field': 'is_main', 'format': '@'}},
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
