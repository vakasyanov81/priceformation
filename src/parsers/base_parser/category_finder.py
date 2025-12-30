"""
ind category, and set
"""

from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder


class CategoryFinder:
    """
    find category, and set
    """

    def __init__(self) -> None:
        """init"""
        self.aliases = AliasContainer(map_categories)
        self._finder = BaseFinder(self.aliases)

    def find(self, item):
        """find"""
        return self.find_in_str(item.title)

    def find_in_str(self, _str: str):
        """find in str"""
        category, bad_category = self._finder.find_word_in_title(_str)
        return category, bad_category


map_categories = {
    "Грузовая шина": "грузовая",
    "Легковая шина": ("легковая", "легкогрузовая", "грязевая"),
    "Спецшина": ("спецшина", "сельхоз"),
    "Мотошина": ("мотошина", "квадроциклы"),
    "Автокамера": ("камеры", "камера", "автокамеры"),
    "Автошина": ("шина", "шины", "автошины"),
    "Диск": ("диски", "автодиск", "автодиски"),
    "Ободная лента": ("о/лента", "лента", "ленты"),
}
