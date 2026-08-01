"""
find manufacturer, make correct manufacturer in title
"""

from typing import Any

from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder, replace_alias_in_title
from parsers.row_item.row_item import RowItem


class ManufacturerFinder:
    """
    find manufacturer, make correct manufacturer in title
    """

    def __init__(self, aliases: dict[str, Any] | None = None) -> None:
        """init"""
        self.aliases = AliasContainer(aliases or {})
        self._finder = BaseFinder(self.aliases)

    def process(self, row_item: RowItem) -> None:
        """process"""

        manufacturer, bad_manufacturer = self._finder.find_word_in_title(row_item.title)

        if bad_manufacturer and manufacturer:
            replace_alias_in_title(row_item, bad_manufacturer, manufacturer)

        # replace manufacturer
        if manufacturer:
            row_item.manufacturer = manufacturer
        elif row_item.manufacturer:
            self.correction_manufacturer(row_item)

    def correction_manufacturer(self, rec: RowItem) -> None:
        """correction manufacturer"""
        self._finder.correction_field(rec, field_name="manufacturer", aliases=self.aliases)
