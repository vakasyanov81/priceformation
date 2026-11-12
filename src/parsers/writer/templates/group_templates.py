"""Размещение штатных прайсов с независимыми схемами товарных групп."""

from dataclasses import replace

from parsers.writer.templates.all_templates import get_writer_template
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput
from parsers.writer.templates.iwrite_template import IWriteTemplate
from parsers.writer.templates.tmpl.for_batteries import ForBatteries
from parsers.writer.templates.tmpl.for_doubles import ForDoubles
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_inner import ForInner

_FIELD = 'field'


def group_template_output(template: type[IWriteTemplate]) -> TemplateOutput:
    """Штатные прайсы включают обе модели с независимыми колонками."""
    output = template().output_spec()
    if template not in {ForInner, ForDrom, ForDoubles}:
        return output
    tires = output.groups[0]
    batteries = ForBatteries().output_spec().groups[0]
    if template in {ForInner, ForDoubles}:
        return replace(
            output,
            mode=OutputMode.WORKBOOK_SHEETS,
            groups=(replace(tires, file_name=None, sheet_name='Шины и диски'), replace(batteries, file_name=None)),
            file_name=tires.file_name,
        )
    batteries = _drom_batteries(batteries)
    return replace(output, groups=(tires, batteries))


def _drom_batteries(group: GroupOutput) -> GroupOutput:
    """Для Дрома выводятся розничная цена и наличие без закупочных данных."""
    return replace(
        group,
        columns=[
            {'Тип товара': {'default_value': 'Аккумулятор'}},
            {'Бренд': {_FIELD: 'manufacturer_name'}},
            {'Номенклатура': {_FIELD: 'title'}},
            {'Цена': {_FIELD: 'sale_price', 'format': '@'}},
            {'Остаток': {_FIELD: 'rest_count'}},
            {'Наличие': {'default_value': 'В наличии'}},
            {'Состояние': {'default_value': 'Новое'}},
            {'Ёмкость, А·ч': {_FIELD: 'capacity_ah'}},
            {'Пусковой ток, А': {_FIELD: 'starting_current_a'}},
            {'Длина, мм': {_FIELD: 'length_mm'}},
            {'Ширина, мм': {_FIELD: 'width_mm'}},
            {'Высота, мм': {_FIELD: 'height_mm'}},
            {'Тип клемм': {_FIELD: 'terminal_type'}},
            {'Типоразмер': {_FIELD: 'size_type'}},
            {'Полярность': {_FIELD: 'polarity'}},
            {'Обслуживаемость': {_FIELD: 'serviceable'}},
            {'Вес': {_FIELD: 'weight'}},
            {'Нижнее крепление': {_FIELD: 'bottom_mount'}},
            {'EFB': {_FIELD: 'efb'}},
            {'AGM': {_FIELD: 'agm'}},
        ],
        filters={'rest_count': [None, '']},
        file_name='price_drom_akb_{now}.xlsx',
    )


def named_group_output(name: str) -> TemplateOutput:
    """Внутренний отчёт дублей использует тот же групповой путь, что и прайсы."""
    template = ForDoubles if name == ForDoubles.template_id else get_writer_template(name)
    return group_template_output(template)
