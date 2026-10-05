"""
write price list interface
"""

from typing import Any


class IXlsDriver:
    """interface for write logic"""

    def add_sheet(self, sheet_name: str) -> IXlsDriver:
        """add sheet with sheet name"""
        raise NotImplementedError

    def write_head(self, names: list[str]) -> None:
        """write head"""
        raise NotImplementedError

    def set_column_format(self, column_format: dict[int, str]) -> None:
        """
        set column format
        :param column_format: dict['column_name', '#,##0.00" ₽"']
        """
        raise NotImplementedError

    def write(
        self,
        row_idx: int,
        col_idx: int,
        cell_content: Any,
        style: Any = None,
        _color: str | None = None,
    ) -> None:
        """write"""
        raise NotImplementedError

    def save(self) -> None:
        """save file"""
        raise NotImplementedError

    def init_workbook(self, _folder: str, _file_name: str) -> Any:
        """init workbook"""
        raise NotImplementedError
