"""
helper for write-column structure
"""

from typing import Any, cast


class ColumnHelper:
    """
    helper for write-column structure
    """

    def __init__(self, col: dict[str, Any]):
        """
        dict with column name and info
        :param col:
        {
            "Тип товара": {
                "style": {
                    "width": 256 * 15
                },
                "field": RowItem.type_production.name
            }
        }
        """
        self._col = col
        first_col = next(iter(col.values()))
        self.column: dict[str, Any] = cast(dict[str, Any], first_col)
        self.name: str = next(iter(col.keys()))
        self.style: dict[str, Any] = self.column.get("style") or {}
        self.style_width: int | None = self.style.get("width")
        self.def_value: str | None = self.column.get("default_value")
        self.field: str | None = self.column.get("field")
        self.skip: bool = bool(self.column.get("skip"))
        self.format: str | None = self.column.get("format")
