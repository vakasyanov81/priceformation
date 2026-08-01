"""
ind category, and set
"""

from typing import Optional, Tuple

from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder
from parsers.row_item.row_item import RowItem


class CategoryFinder:
    """
    find category, and set
    """

    def __init__(self) -> None:
        """init"""
        self.aliases = AliasContainer(map_categories)
        self._finder = BaseFinder(self.aliases)

    def find(self, row_item: RowItem) -> Tuple[Optional[str], Optional[str]]:
        """find"""
        return self.find_in_str(row_item.title)

    def find_in_str(self, _str: str) -> Tuple[Optional[str], Optional[str]]:
        """find in str"""
        category, bad_category = self._finder.find_word_in_title(_str)
        return category, bad_category


map_categories: dict[str, tuple[str, ...] | str] = {
    "Грузовая шина": "грузовая",
    "Легковая шина": ("легковая", "легкогрузовая", "грязевая"),
    "Спецшина": ("спецшина", "сельхоз"),
    "Мотошина": ("мотошина", "квадроциклы"),
    "Автокамера": ("камеры", "камера", "автокамеры"),
    "Автошина": ("шина", "шины", "автошины"),
    "Диск": ("диски", "автодиск", "автодиски"),
    "Ободная лента": ("о/лента", "лента", "ленты"),
}
