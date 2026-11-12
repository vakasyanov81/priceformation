"""Общая книга с независимыми листами шин, дисков и аккумуляторов."""

from dataclasses import replace

from parsers.writer.templates.group_output import OutputMode, TemplateOutput
from parsers.writer.templates.tmpl.for_batteries import ForBatteries
from parsers.writer.templates.tmpl.for_full import ForFull


class ForProductGroups(ForFull):
    """Полные данные двух групп в одной книге."""

    template_id = 'for_product_groups'

    def output_spec(self) -> TemplateOutput:
        tires = ForFull().output_spec().groups[0]
        batteries = ForBatteries().output_spec().groups[0]
        return TemplateOutput(
            self.template_id,
            OutputMode.WORKBOOK_SHEETS,
            (replace(tires, file_name=None, sheet_name='Шины и диски'), replace(batteries, file_name=None)),
            'price_{now}.xlsx',
        )
