"""
find word in title
"""

from functools import lru_cache
from typing import Optional, Tuple

from parsers.row_item.row_item import RowItem

from .alias_container import AliasContainer


@lru_cache()
def str_lower(_str: str) -> str:
    """cached lowered string"""
    return _str.lower()


def replace_alias_in_title(row_item: RowItem, old_man: str, new_man: str) -> None:
    """replace manufacturer in title chunks"""
    row_item.title = row_item.title.replace(old_man, new_man)


class BaseFinder:
    """
    find word in title
    """

    def __init__(self, alias_container: AliasContainer) -> None:
        """init"""
        self.alias_container = alias_container
        self._title: str | None = None
        self._incorrect_lowers: list[str] = self.alias_container.incorrect_words_lower
        self._correct_lowers: list[str] = self.alias_container.all_correct_words_lower
        self._aliases: dict[str, str] = self.alias_container.reversed_map

    @property
    def title_lower(self) -> Optional[str]:
        """lowercase title"""
        return self._title.lower() if self._title else self._title

    def find_word_in_title(self, title: str) -> Tuple[Optional[str], Optional[str]]:
        """find substring in title"""
        self._title = title
        correct_alias, incorrect_alias = self._find_from_lower_list(self._correct_lowers, return_correct=True)
        if correct_alias:
            return correct_alias, incorrect_alias
        return self._find_from_lower_list(self._incorrect_lowers)

    def _find_from_lower_list(
        self,
        _lowers_list: list[str],
        return_correct: bool = False,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        find by incorrect aliases in title
        :return (correct alias, founded incorrect alias)
        ex: Adidas, abibas
        """
        match = self._match_lower_alias(_lowers_list)
        if match is None:
            return None, None

        if return_correct:
            return self.alias_container.all_correct_words[match[2]], match[1]
        return self._aliases.get(match[0]), match[1]

    def _match_lower_alias(self, _lowers_list: list[str]) -> Optional[Tuple[str, str, int]]:
        """Найти первое совпадение алиаса в title."""
        title = self._title
        if title is None:
            return None
        for index, lower_alias in enumerate(_lowers_list):
            found_position = self._find(lower_alias)
            if found_position == -1:
                continue
            return (
                _lowers_list[index],
                title[found_position : found_position + len(lower_alias)],
                index,
            )
        return None

    def _find(self, lower_alias: str) -> int:
        """find alias wrapped whitespace in title, and find in start title, and find in end title"""
        white_space = " "
        title_lower = self.title_lower
        if not title_lower:
            return -1
        position = title_lower.find(white_space + lower_alias + white_space)
        if position != -1:
            return position + 1

        alias_len = len(lower_alias)
        if title_lower[:alias_len] == lower_alias:
            return 0

        suffix = white_space + lower_alias
        if len(title_lower) > alias_len and title_lower.endswith(suffix):
            return len(title_lower) - alias_len
        return -1

    def correction_field(self, rec: RowItem, field_name: str, aliases: AliasContainer) -> None:
        """replace property in rec if it has bad signature"""
        l_man = str_lower(getattr(rec, field_name))
        correct = aliases.reversed_map.get(l_man)
        if not correct:
            return
        setattr(rec, field_name, correct)
