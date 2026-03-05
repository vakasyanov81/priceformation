"""
write price list logic
"""

import datetime
from pathlib import Path

from cfg import init_cfg
from parsers.writer.ixls_driver import IXlsDriver
from parsers.writer.templates.column_helper import ColumnHelper
from parsers.writer.templates.iwrite_template import IWriteTemplate

config = init_cfg()


def get_value(column: dict, row_item: dict) -> str | None:
    """get value for write cell"""
    col = ColumnHelper(column)
    if col.skip:
        return None

    raw_value = row_item.get(col.field) or col.def_value
    return _to_str(raw_value)


def _to_str(raw_value) -> str:
    """list to string"""
    if isinstance(raw_value, list):
        filtered_items = [element for element in raw_value if element]
        return ", ".join(filtered_items)

    return raw_value


def make_exclude(products: list, exclude: dict) -> list:
    """filtration"""
    if not exclude:
        return products

    included = []
    for field, ex_values in exclude.items():
        for product in products:
            if product.get(field) not in ex_values:
                included.append(product)
    return included


def get_result_folder_name() -> str:
    return config.main.result_folder_path


def create_result_folder():
    """create result folder"""
    if not Path(get_result_folder_name()).exists():
        Path(get_result_folder_name()).mkdir(parents=True)


class XlsWriter:
    """price writer"""

    def __init__(self, driver, parse_result: list, template):
        """init"""
        self.driver: IXlsDriver = driver
        self.template: IWriteTemplate = template()
        self.exclude = self.template.exclude()
        create_result_folder()
        self.driver.init_workbook(config.main.result_folder_path, self.get_file_name())
        self.driver.add_sheet("price")
        self.parse_result = parse_result
        self.driver.set_column_format(self.template.get_columns_format())
        self.write()

    def write(self):
        """make write"""
        # write header
        self.driver.write_head(self.col_names())

        # write body
        filtered_data = make_exclude(self.parse_result, self.exclude)
        for row_index, product in enumerate(filtered_data):
            self._write_row(product, row_index, self._get_color(product))

        # save workbook
        self.driver.save()

    def get_file_name(self):
        """get file name for writing"""
        file_template = self.template.get_file_name()
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return file_template.format(now=current_date)

    def col_names(self) -> list:
        """get column names"""
        names = []
        for col in self.template.columns():
            names.append(ColumnHelper(col).name)
        return names

    def _get_color(self, product) -> tuple[str | None, int | None]:
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

    def _write_row(self, row_item, row_index, color: tuple | None = None):
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
