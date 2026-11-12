"""
write price list logic
"""

import datetime
from pathlib import Path
from typing import Any

from parsers.writer.ixlsx_driver import IXlsDriver
from parsers.writer.row_style import PriceRow, RowColor, cell_color, row_colors, write_legend
from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.iwrite_template import IWriteTemplate

type CellValue = str | int | float | None

_PRICE_FIELDS = frozenset(('price_opt', 'price_markup', 'price_recommended', 'sale_price'))


def get_value(column: dict[str, Any], row_item: PriceRow) -> CellValue:
    """get value for write cell"""
    return cell_value(ColumnHelper(column), row_item)


def cell_value(col: ColumnHelper, row_item: PriceRow) -> CellValue:
    """Значение ячейки по уже разобранной колонке: helper строится раз на колонку, а не на каждую ячейку."""
    if col.skip:
        return None

    field_name = col.field
    raw_value = row_item.get(field_name) if field_name else None
    if raw_value is True and col.true_value:
        raw_value = col.true_value
    raw_value = raw_value or col.def_value
    cell_value = _to_str(raw_value)
    if field_name in _PRICE_FIELDS and isinstance(cell_value, float) and cell_value.is_integer():
        cell_value = int(cell_value)
    if col.suffix and col.suffix_when and row_item.get(col.suffix_when):
        prefix = cell_value or ''
        return f'{prefix}{col.suffix}'
    return cell_value


def _to_str(raw_value: CellValue | list[str]) -> CellValue:
    """Список — в строку через запятую; скаляр ячейки (str, число, None) остаётся как есть."""
    if isinstance(raw_value, list):
        filtered_items = [element for element in raw_value if element]
        return ', '.join(filtered_items)

    return raw_value


def has_value(cell: object) -> bool:
    """значение, которое попадает в вывод; общее правило для xlsx и jsonl

    get_value отбрасывает falsy-значения поля (0, False, '', []) ещё до вызова,
    поэтому falsy сюда доходит только из default_value. Считаем его отсутствующим:
    в xlsx такая ячейка остаётся пустой, и jsonl не должен добавлять ключ, которого
    в xlsx нет.
    """
    return bool(cell)


def _passes_exclude(product: PriceRow, exclude: dict[str, Any]) -> bool:
    """позиция не отбрасывается ни одним правилом exclude"""
    rules = exclude.items()
    return all(product.get(field) not in ex_values for field, ex_values in rules)


def make_exclude(products: list[PriceRow], exclude: dict[str, Any]) -> list[PriceRow]:
    """filtration: позиция попадает в вывод, только если проходит все правила exclude"""
    if not exclude:
        return products

    return [product for product in products if _passes_exclude(product, exclude)]


class XlsWriter:
    """price writer"""

    def __init__(
        self,
        driver: IXlsDriver,
        parse_result: list[PriceRow],
        template: type[IWriteTemplate] | IWriteTemplate,
        *,
        result_folder: str,
    ) -> None:
        """init"""
        self.driver: IXlsDriver = driver
        self.template = template() if isinstance(template, type) else template
        self.exclude = self.template.exclude()
        self.parse_result = parse_result
        self._result_folder = result_folder

    def write(self) -> None:
        """Create result folder, fill workbook, save."""
        Path(self._result_folder).mkdir(parents=True, exist_ok=True)
        self.driver.init_workbook(self._result_folder, self.get_file_name())
        self.write_sheet()
        self.driver.save()

    def write_sheet(self) -> None:
        """Заполнить отдельный лист уже открытой книги без сохранения."""
        self.driver.add_sheet(self.template.get_sheet_name())
        self.driver.set_column_format(self.template.get_columns_format())
        legend = self.template.colors().get('legend') or []
        offset = write_legend(self.driver, legend)
        helpers = [ColumnHelper(col) for col in self.template.columns()]
        self.driver.write_head([col.name for col in helpers], offset)
        for row_index, product in enumerate(make_exclude(self.parse_result, self.exclude), start=offset):
            self._write_row(product, row_index, helpers, self._get_color(product))

    def get_file_name(self) -> str:
        """get file name for writing"""
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        return self.template.resolve_file_name(current_date)

    def get_result_path(self) -> str:
        """Absolute path of the written file."""
        return str(Path(self._result_folder, self.get_file_name()).resolve())

    def _get_color(self, product: PriceRow) -> list[RowColor]:
        """get colors: правила, подошедшие строке, по приоритету"""
        return row_colors(self.template.colors(), product)

    def _write_row(
        self,
        row_item: PriceRow,
        row_index: int,
        helpers: list[ColumnHelper],
        colors: list[RowColor] | None = None,
    ) -> None:
        """write row item"""
        for col_index, col in enumerate(helpers):
            cell = cell_value(col, row_item)
            if not has_value(cell):
                continue

            # индекс колонки None в настройке цвета — красим всю строку
            self.driver.write(
                row_index + 1,
                col_index,
                cell,
                _color=cell_color(colors or [], col_index),
            )
