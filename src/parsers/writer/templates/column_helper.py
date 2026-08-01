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

    @property
    def column(self) -> dict[str, Any]:
        """
        dict with column info
        :return:
        {
            "style": {
                "width": 256 * 15
            },
            "field": RowItem.type_production.name
        }
        """
        return cast(dict[str, Any], list(self._col.values())[0])

    @property
    def name(self) -> str:
        """
        column name
        :return: "Тип товара"
        """
        return list(self._col.keys())[0]

    @property
    def style(self) -> dict[str, Any]:
        """column style"""
        return self.column.get("style") or {}

    @property
    def style_width(self) -> int | None:
        """column width"""
        return self.style.get("width")

    @property
    def def_value(self) -> str | None:
        """default value"""
        return self.column.get("default_value")

    @property
    def field(self) -> str | None:
        """filed name in data-row for write"""
        return self.column.get("field")

    @property
    def skip(self) -> bool:
        """if True, then skip column"""
        return bool(self.column.get("skip"))

    @property
    def format(self) -> str | None:
        """default value"""
        return self.column.get("format")
