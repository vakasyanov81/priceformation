"""
write price list logic via xlsxwriter module
"""

import openpyxl
from openpyxl.styles import Color, Font, PatternFill

from cfg import init_cfg

from .ixls_driver import IXlsDriver

config = init_cfg()

EXCEL_ALPHABET_SIZE = 26
EXCEL_COLUMN_A_ORD = 65


class XlsxWriterDriver(IXlsDriver):
    """
    write price list logic via openpyxl module
    """

    def __init__(self):
        """init"""
        self.work_book = None
        self.work_sheet = None
        self.current_col_index = 0
        self.current_row_index = 0
        self.col_max_length = {}
        self._file_name = None
        self.row_index_at = 1

    def init_workbook(self, _folder: str, _file_name: str):
        if not self.work_book:
            self._file_name = _folder + _file_name
            self.work_book = openpyxl.Workbook()

        return self.work_book

    def get_workbook(self):
        """get workbook"""
        return self.work_book

    def add_sheet(self, sheet_name):
        sheet = self.get_workbook().active
        sheet.title = sheet_name
        self.work_sheet = sheet
        return self

    def write_head(self, names):
        """write head"""

        for col_idx, name in enumerate(names):
            self.write(0, col_idx, name, style=Font(bold=True))

    def set_column_format(self, column_format: dict[int, str]):
        """
        set column format
        :param column_format: dict[column_index, '@']
        """
        for index, c_format in column_format.items():
            self.work_sheet.column_dimensions[self.number_to_excel_column(index)].number_format = c_format

    def write(self, row_idx, col_idx, _value, style=None, _color: str = None):
        """write"""
        row_idx += self.row_index_at
        col_idx += self.row_index_at
        cell = self.work_sheet.cell(row=row_idx, column=col_idx, value=_value)
        if style:
            cell.font = style
        if _color:
            cell.fill = PatternFill(fgColor=Color(rgb=_color.lstrip("#")), fill_type="solid")

        self.current_col_index = col_idx
        self.current_row_index = row_idx
        value_length = len(str(_value or ""))
        if self.col_max_length.get(col_idx) is None or self.col_max_length[col_idx] < value_length:
            self.col_max_length[col_idx] = value_length

    def save(self):
        """save file"""
        self.set_auto_width()
        self.get_workbook().save(self._file_name)
        self.get_workbook().close()

    @classmethod
    def number_to_excel_column(cls, number: int) -> str:
        """
        Конвертирует номер колонки в символьное обозначение Excel
        1 -> A, 2 -> B, ..., 26 -> Z, 27 -> AA, и т.д.
        """
        result = ""
        while number > 0:
            number, remainder = divmod(number - 1, EXCEL_ALPHABET_SIZE)
            result = chr(EXCEL_COLUMN_A_ORD + remainder) + result
        return result

    def set_auto_width(self):
        """set auto width by content"""

        for col_index, max_len in self.col_max_length.items():
            self.work_sheet.column_dimensions[self.number_to_excel_column(col_index)].width = max_len + 4
