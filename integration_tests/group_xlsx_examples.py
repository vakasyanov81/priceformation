"""Сборка двух тестовых моделей и шаблонов для интеграционной проверки XLSX."""

from dataclasses import replace
from pathlib import Path

from domain.product_group_result import ProductGroupResult, TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from integration_tests.product_group_examples import OtherStrategy, TireStrategy, read_group, supplier_price
from parsers.common_price.tire_output import TireOutputSource
from parsers.writer.output_plan import GroupOutputSource
from parsers.writer.templates.group_output import GroupOutput, OutputMode, TemplateOutput
from tests.group_output_examples import OtherOutputSource
from tests.test_domain.group_handler_examples import TestGroupResult, TestPosition

TIRES = ProductGroup.TIRE_AND_DISK
OTHER = ProductGroup.BATTERIES
DATE = '2026-11-12'
_NO_EMPTY: frozenset[ProductGroup] = frozenset()
_TITLE = 'title'


def output_sources(path: Path, empty: frozenset[ProductGroup] = _NO_EMPTY) -> dict[ProductGroup, GroupOutputSource]:
    """Прочитать реальный XLSX и сохранить модели до подготовки выхода."""
    supplier_price(path)
    tire_package: ProductGroupResult[RowItem] = read_group(path, TireStrategy(), {0: _TITLE, 2: 'price_opt'})
    other_package: ProductGroupResult[TestPosition] = read_group(path, OtherStrategy(), {1: 'label'})
    return {
        TIRES: TireOutputSource(TireAndDiskResult(() if TIRES in empty else tire_package.positions)),
        OTHER: OtherOutputSource(TestGroupResult(() if OTHER in empty else other_package.positions)),
    }


def output_template(mode: OutputMode) -> TemplateOutput:
    """Одинаковые правила групп при разном размещении результата."""
    tires = GroupOutput(
        TIRES,
        'Шины',
        [
            {'Название': {'field': _TITLE, 'format': '@'}},
            {'Цена': {'field': 'price_opt', 'format': '#,##0.00'}},
        ],
        {_TITLE: ['DIFFERENT']},
        {'by_column': _TITLE, 'with_map': {'SAME': '00FF00'}},
        file_name='tires_{now}.xlsx',
    )
    other = GroupOutput(
        OTHER,
        'Тестовая модель',
        [{'Метка': {'field': 'label', 'format': '@'}}],
        {'label': ['other']},
        {},
        file_name='other_{now}.xlsx',
    )
    if mode is OutputMode.WORKBOOK_SHEETS:
        return TemplateOutput(
            'integration', mode, (replace(tires, file_name=None), replace(other, file_name=None)), 'all_{now}.xlsx'
        )
    return TemplateOutput('integration', mode, (tires, other))
