"""
write price list logic via xlwt module
"""

from .ixls_driver import IXlsDriver


class FakeXlwtDriver(IXlsDriver):
    """
    fake write price list logic
    """

    def __init__(self):
        """init"""
        self.work_sheet = None
        self.sheet_name = None
        self.width = {}
        self.head = []
        self.body = {}
        self.file_name = None
        self.folder = None

    def add_sheet(self, sheet_name):
        self.sheet_name = sheet_name
        return self

    def set_width(self, col_index: int, col_width: int):
        """set width"""

        self.width[col_index] = col_width

    def write_head(self, names):
        """write head"""
        self.head = names

    def write(self, row_idx, col_idx, cell_content, style=None, _color=None):
        """write"""
        self.body[f"cell({row_idx},{col_idx})"] = cell_content

    def init_workbook(self, _folder: str, _file_name: str):
        self.file_name = _file_name
        self.folder = _folder

    def save(self):
        """save file"""

    def set_column_format(self, column_format: dict[int, str]):
        """
        set column format
        :param column_format: dict['column_name', '#,##0.00" ₽"']
        """
        return {}

    def __repr__(self):
        return (
            f"\n--FakeXlwtDriver--\n"
            f"filename: {self.file_name}\n"
            f"folder: {self.folder}\n"
            f"sheet_name: {self.sheet_name}\n"
            f"col_width: {self.width}\n"
            f"head: {self.head}\n"
            f"body: {self.body}\n"
        )

    def get_folder(self) -> str:
        """folder for fake workbook"""
        return self.folder or ""
