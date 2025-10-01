# -*- coding: utf-8 -*-
"""
container for aliases
"""
__author__ = "Kasyanov V.A."

from functools import lru_cache

CorrectWord, CorrectLoweredWord, IncorrectLoweredAlias = str, str, str


class AliasContainer:
    """
    container for aliases
    """

    def __init__(self, map_aliases: dict[CorrectWord, tuple[IncorrectLoweredAlias]]):
        """
        :param map_aliases: {
            correct_word_1: (
                incorrect_alias_in_lowercase_1,
                incorrect_alias_in_lowercase_2,
                ...
            ),
            correct_word_2: ...
        }
        """
        self.map_aliases = map_aliases

    @property
    @lru_cache()
    def reversed_map(self) -> dict[IncorrectLoweredAlias, CorrectWord]:
        """
        :return {
            incorrect_alias_in_lowercase_1: correct_word_1,
            incorrect_alias_in_lowercase_2: correct_word_1,
            incorrect_alias_in_lowercase_3: correct_word_2,
            ...
        }
        """
        reversed_map = {}
        for correct_name, incorrect_names in self.map_aliases.items():
            if isinstance(incorrect_names, str):
                incorrect_names = (incorrect_names,)
            reversed_map.update({incorrect_name.lower(): correct_name for incorrect_name in incorrect_names})
        return reversed_map

    @property
    @lru_cache()
    def all_correct_words(self) -> list[CorrectWord]:
        """collected all correct words"""
        return self.sort_by_length(list(self.map_aliases.keys()))

    @property
    @lru_cache()
    def all_correct_words_lower(self) -> list[CorrectLoweredWord]:
        """collected all correct words in lowercase"""
        return self.to_lowercase(self.all_correct_words)

    @property
    @lru_cache()
    def incorrect_words(self) -> list:
        """collected all incorrect words"""
        return self.sort_by_length(list(self.reversed_map.keys()))

    @property
    @lru_cache()
    def incorrect_words_lower(self) -> list[IncorrectLoweredAlias]:
        """collected all incorrect words in lowercase"""
        return self.to_lowercase(self.incorrect_words)

    @property
    @lru_cache()
    def correct_words(self) -> list:
        """collected all correct words"""
        return self.sort_by_length(list(self.reversed_map.values()))

    @property
    @lru_cache()
    def correct_words_lower(self) -> list:
        """collected all correct words in lowercase"""
        return self.to_lowercase(self.correct_words)

    @classmethod
    def to_lowercase(cls, words: list[str]) -> list[str]:
        """list-str to lowercase"""
        return [word.lower() for word in words]

    @classmethod
    def sort_by_length(cls, _list: list[str]) -> list[str]:
        """Sort by length. Longer words in first"""
        _list.sort(key=len, reverse=True)
        return _list
