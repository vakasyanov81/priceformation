"""
write price list logic via xlwt module
"""

from typing import Any

from .ixls_driver import IXlsDriver


class FakeXlwtDriver(IXlsDriver):
    """
    fake write price list logic
    """

    def __init__(self) -> None:
        """init"""
        self.work_sheet = None
        self.sheet_name: str | None = None
        self.width: dict[int, int] = {}
        self.head: list[str] = []
        self.body: dict[str, Any] = {}
        self.file_name: str | None = None
        self.folder: str | None = None

    def add_sheet(self, sheet_name: str) -> FakeXlwtDriver:
        self.sheet_name = sheet_name
        return self

    def write_head(self, names: list[str]) -> None:
        """write head"""
        self.head = names

    def write(
        self,
        row_idx: int,
        col_idx: int,
        cell_content: Any,
        style: Any = None,
        _color: str | None = None,
    ) -> None:
        """write"""
        self.body[f"cell({row_idx},{col_idx})"] = cell_content

    def init_workbook(self, _folder: str, _file_name: str) -> None:
        self.file_name = _file_name
        self.folder = _folder

    def save(self) -> None:
        """save file"""

    def set_column_format(self, column_format: dict[int, str]) -> None:
        """
        set column format
        :param column_format: dict['column_name', '#,##0.00" ₽"']
        """
