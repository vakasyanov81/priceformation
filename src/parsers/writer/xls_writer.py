"""
write price list logic
"""

import datetime
from pathlib import Path
from typing import Optional, Tuple

from cfg import init_cfg
from parsers.writer.templates.iwrite_template import IWriteTemplate
from .ixls_driver import IXlsDriver
from .templates.column_helper import ColumnHelper

config = init_cfg()


class XlsWriter:
    """price writer"""

    __FOLDER__ = f"file_prices{config.main.sep}result{config.main.sep}"

    def __init__(self, driver, parse_result: list, template) -> None:
        """init"""
        self.driver: IXlsDriver = driver
        self.template: IWriteTemplate = template()
        self.exclude = self.template.exclude()
        self.create_folder()
        self.driver.init_workbook(self.__FOLDER__, self.get_file_name())
        self.driver.add_sheet("price")
        self.data = parse_result
        self.driver.set_column_format(self.template.get_columns_format())
        self.write()

    def create_folder(self) -> None:
        """create result folder"""
        if not Path(self.__FOLDER__).exists():
            Path(self.__FOLDER__).mkdir(parents=True)

    def write(self) -> None:
        """make write"""
        self.driver.write_head(self.col_names())
        self.write_body()

        # сохраняем рабочую книгу
        self.driver.save()

    def get_file_name(self):
        """get file name for writing"""
        return self.template.get_file_name().format(now=datetime.datetime.now().strftime("%Y-%m-%d"))

    def col_names(self) -> list:
        """get column names"""
        names = []
        for col in self.template.columns():
            names.append(ColumnHelper(col).name)
        return names

    def write_body(self) -> None:
        """write body"""
        data = self.make_exclude()
        for row_index, item in enumerate(data):
            self.write_row(item, row_index, self.get_color(item))

    def get_color(self, item) -> Tuple[Optional[str], Optional[int]]:
        """get color"""
        colors = self.template.colors()
        empty = None, None
        if not colors:
            return empty
        column_name = colors.get("by_column")
        color_map = colors.get("with_map")
        index = colors.get("set_to_column_index")
        if not column_name or not color_map or column_name not in item:
            return empty

        column_value = item.get(column_name)
        if not column_value:
            return empty
        return color_map.get(column_value), index

    def write_row(self, row_item, row_index, color: Tuple = None) -> None:
        """write row item"""
        color_index = color[1] if color else 0
        _color = color[0] if color else None
        for col_index, col in enumerate(self.template.columns()):
            val = self.get_value(col, row_item)

            if not val:
                continue

            _style = _color if color_index == col_index else None

            self.driver.write(row_index + 1, col_index, val, _color=_style)

    @classmethod
    def get_value(cls, column: dict, row_item):
        """get value for write cell"""
        col = ColumnHelper(column)
        if col.skip:
            return None

        value = row_item.get(col.field) or col.def_value
        return cls._to_str(value)

    @classmethod
    def _to_str(cls, value) -> str:
        """list to string"""
        if isinstance(value, list):
            val = [v for v in value if v]
            return ", ".join(val)

        return value

    def make_exclude(self):
        """filtration"""
        included = []

        if not self.exclude:
            return self.data

        for field, ex_values in self.exclude.items():
            for item in self.data:
                if item.get(field) not in ex_values:
                    included.append(item)
        return included
