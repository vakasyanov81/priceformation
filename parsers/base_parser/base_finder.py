# -*- coding: utf-8 -*-
"""
find word in title
"""
__author__ = "Kasyanov V.A."

from functools import lru_cache
from typing import AnyStr, Optional, Tuple

from parsers.row_item.row_item import RowItem

from .alias_container import AliasContainer


class BaseFinder:
    """
    find word in title
    """

    def __init__(self, alias_container: AliasContainer):
        """init"""
        self.alias_container = alias_container
        self._title = None
        self._incorrect_lowers: list = self.alias_container.incorrect_words_lower
        self._correct_lowers: list = self.alias_container.all_correct_words_lower
        self._incorrect: list = self.alias_container.incorrect_words
        self._correct: list = self.alias_container.correct_words
        self._aliases: dict = self.alias_container.reversed_map

    @property
    def title_lower(self):
        """lowercase title"""
        return self._title.lower() if self._title else self._title

    def find_word_in_title(self, title) -> Tuple[Optional[AnyStr], Optional[AnyStr]]:
        """find substring in title"""
        self._title = title

        correct_alias, incorrect_alias = self.find_correct()

        if correct_alias:
            return correct_alias, incorrect_alias

        return self.find_incorrect()

    def find_incorrect(self) -> Tuple[Optional[AnyStr], Optional[AnyStr]]:
        """
        find by incorrect aliases in title
        :return (correct alias, founded incorrect alias)
        ex: Adidas, abibas
        """
        return self._find_from_lower_list(self._incorrect_lowers)

    def find_correct(self) -> Tuple[Optional[AnyStr], Optional[AnyStr]]:
        """
        find by correct aliases in title
        :return (correct alias, founded correct alias in other register)
        ex: Adidas, adidas
        """
        return self._find_from_lower_list(self._correct_lowers, return_correct=True)

    def _find_from_lower_list(
        self, _lowers_list: list, return_correct=False
    ) -> Tuple[Optional[AnyStr], Optional[AnyStr]]:
        """
        find by incorrect aliases in title
        :return (correct alias, founded incorrect alias)
        ex: Adidas, abibas
        """
        result_name = None
        founded_word = None
        index = None

        for index, _lower_alias in enumerate(_lowers_list):
            found_position = self._find(_lower_alias)
            if found_position != -1:
                result_name = _lowers_list[index]
                next_position = found_position + len(_lower_alias)
                founded_word = self._title[found_position:next_position]
                break

        if not result_name:
            return None, None

        result = self.alias_container.all_correct_words[index] if return_correct else self._aliases.get(result_name)

        return result, founded_word

    def _find(self, lower_alias) -> int:
        """find alias wrapped whitespace in title, and find in start title, and find in end title"""
        white_space = " "
        if not self.title_lower:
            return -1
        position = self.title_lower.find(white_space + lower_alias + white_space)
        if position != -1:
            return position + 1

        alias_len = len(lower_alias)
        title_len = len(self.title_lower)

        if self.title_lower[0:alias_len] == lower_alias:
            return 0

        if alias_len >= title_len:
            return -1

        if self.title_lower[(title_len - alias_len - 1) : title_len] == white_space + lower_alias:
            return title_len - alias_len

        return -1

    @classmethod
    def replace_alias_in_title(cls, item: RowItem, old_man, new_man):
        """replace manufacturer in title chunks"""
        item.title = item.title.replace(old_man, new_man)

    def correction_field(self, rec: RowItem, field_name, aliases):
        """replace property in rec if it has bad signature"""
        l_man = self.str_lower(getattr(rec, field_name))
        if l_man not in aliases.incorrect_words_lower:
            return
        index = aliases.incorrect_words_lower.index(l_man)
        setattr(rec, field_name, aliases.correct_words_lower[index])

    @classmethod
    @lru_cache()
    def str_lower(cls, _str: str):
        """cached lowered string"""
        return _str.lower()
