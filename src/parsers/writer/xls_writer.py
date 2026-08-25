"""
write price list logic
"""

import datetime
from pathlib import Path
from typing import Any

from parsers.writer.ixls_driver import IXlsDriver
from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.iwrite_template import IWriteTemplate

type RowColor = tuple[str | None, int | None]
type PriceRow = dict[str, Any]


def get_value(column: dict[str, Any], row_item: PriceRow) -> str | None:
    """get value for write cell"""
    col = ColumnHelper(column)
    if col.skip:
        return None

    field_name = col.field
    raw_value = row_item.get(field_name) if field_name else None
    raw_value = raw_value or col.def_value
    return _to_str(raw_value)


def _to_str(raw_value: object) -> str:
    """list to string"""
    if isinstance(raw_value, list):
        filtered_items = [element for element in raw_value if element]
        return ", ".join(filtered_items)

    return raw_value  # type: ignore[return-value]


def make_exclude(products: list[PriceRow], exclude: dict[str, Any]) -> list[PriceRow]:
    """filtration"""
    if not exclude:
        return products

    included: list[PriceRow] = []
    for field, ex_values in exclude.items():
        included.extend(product for product in products if product.get(field) not in ex_values)
    return included


class XlsWriter:
    """price writer"""

    def __init__(
        self,
        driver: IXlsDriver,
        parse_result: list[PriceRow],
        template: type[IWriteTemplate],
        *,
        result_folder: str,
    ) -> None:
        """init"""
        self.driver: IXlsDriver = driver
        self.template: IWriteTemplate = template()
        self.exclude = self.template.exclude()
        self.parse_result = parse_result
        self._result_folder = result_folder

    def write(self) -> None:
        """Create result folder, fill workbook, save."""
        folder = Path(self._result_folder)
        folder.mkdir(parents=True, exist_ok=True)
        self.driver.init_workbook(str(folder), self.get_file_name())
        self.driver.add_sheet("price")
        self.driver.set_column_format(self.template.get_columns_format())
        self.driver.write_head(self.col_names())
        filtered_data = make_exclude(self.parse_result, self.exclude)
        for row_index, product in enumerate(filtered_data):
            self._write_row(product, row_index, self._get_color(product))
        self.driver.save()

    def get_file_name(self) -> str:
        """get file name for writing"""
        file_template = self.template.get_file_name()
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return file_template.format(now=current_date)

    def get_result_path(self) -> str:
        """Absolute path of the written file."""
        return str(Path(self._result_folder, self.get_file_name()).resolve())

    def col_names(self) -> list[str]:
        """get column names"""
        return [ColumnHelper(col).name for col in self.template.columns()]

    def _get_color(self, product: PriceRow) -> RowColor:
        """get color"""
        colors = self.template.colors()
        if not colors:
            return None, None

        column_name = colors.get("by_column")
        if not column_name or column_name not in product:
            return None, None

        column_value = product.get(column_name)
        if not column_value:
            return None, None

        color_map = colors.get("with_map")
        if not color_map:
            return None, None

        index = colors.get("set_to_column_index")
        return color_map.get(column_value), index

    def _write_row(self, row_item: PriceRow, row_index: int, color: RowColor | None = None) -> None:
        """write row item"""
        for col_index, col in enumerate(self.template.columns()):
            cell_value = get_value(col, row_item)
            if not cell_value:
                continue

            cell_color = color[0] if color and color[1] == col_index else None
            self.driver.write(
                row_index + 1,
                col_index,
                cell_value,
                _color=cell_color,
            )
