"""
ind category, and set
"""

from typing import Optional, Sequence, Tuple

from parsers.base_parser.alias_container import AliasContainer
from parsers.base_parser.base_finder import BaseFinder
from parsers.row_item.row_item import RowItem

_UNKNOWN_TYPE_LABEL = "не указан"
_MSG_SKIPPED_CATEGORIES = (
    "Пропущено {count} позиций у поставщиков ({suppliers}) из-за невозможности сопоставить категории ({categories})."
)


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

    def find_canonical(self, raw_type: str | None) -> str | None:
        """Return a known product type for a supplier category, if any."""
        if raw_type is None:
            return None
        normalized = raw_type.strip()
        if not normalized:
            return None
        category, _unused_alias = self.find_in_str(normalized)
        return category


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


def canonical_product_type(
    raw_type: str | None,
    finder: CategoryFinder | None = None,
) -> str | None:
    """Map a supplier category to a known product type."""
    return (finder or CategoryFinder()).find_canonical(raw_type)


def raw_category_label(raw_type: str | None) -> str:
    """Human-readable supplier category for skip reports."""
    if raw_type is None:
        return _UNKNOWN_TYPE_LABEL
    stripped = raw_type.strip()
    if stripped:
        return stripped
    return _UNKNOWN_TYPE_LABEL


def _joined_unique(labels: Sequence[str]) -> str:
    """Join unique values in stable order."""
    return ", ".join(sorted(set(labels)))


def skipped_unknown_categories_message(skips: Sequence[tuple[str, str]]) -> str | None:
    """Summary of rows skipped because the supplier category is unknown."""
    if not skips:
        return None
    suppliers, categories = zip(*skips, strict=True)
    return _MSG_SKIPPED_CATEGORIES.format(
        count=len(skips),
        suppliers=_joined_unique(suppliers),
        categories=_joined_unique(categories),
    )
