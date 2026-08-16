"""
container for aliases
"""

from functools import cached_property
from typing import TypeAlias

CorrectWord: TypeAlias = str
CorrectLoweredWord: TypeAlias = str
IncorrectLoweredAlias: TypeAlias = str


def to_lowercase(words: list[str]) -> list[str]:
    """list-str to lowercase"""
    return [word.lower() for word in words]


def sort_by_length(_list: list[str]) -> list[str]:
    """Sort by length. Longer words in first"""
    _list.sort(key=len, reverse=True)
    return _list


def _alias_entries(
    correct_name: CorrectWord,
    incorrect_names: tuple[IncorrectLoweredAlias, ...] | IncorrectLoweredAlias,
    reserved_keys: set[str],
) -> dict[IncorrectLoweredAlias, CorrectWord]:
    if isinstance(incorrect_names, str):
        incorrect_names = (incorrect_names,)
    blocked = reserved_keys - {correct_name.lower()}
    entries: dict[IncorrectLoweredAlias, CorrectWord] = {}
    for alias in incorrect_names:
        if not alias.strip():
            continue
        if alias.lower() in blocked:
            continue
        entries[alias.lower()] = correct_name
    return entries


def build_reversed_map(
    map_aliases: dict[CorrectWord, tuple[IncorrectLoweredAlias, ...] | IncorrectLoweredAlias],
) -> dict[IncorrectLoweredAlias, CorrectWord]:
    """incorrect alias -> correct word; other brands' canonical names are not aliases."""
    reserved_keys = {name.lower() for name in map_aliases}
    reversed_map: dict[IncorrectLoweredAlias, CorrectWord] = {}
    for correct_name, incorrect_names in map_aliases.items():
        reversed_map.update(_alias_entries(correct_name, incorrect_names, reserved_keys))
    return reversed_map


class AliasContainer:
    """
    container for aliases
    """

    def __init__(self, map_aliases: dict[CorrectWord, tuple[IncorrectLoweredAlias, ...] | IncorrectLoweredAlias]):
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

    @cached_property
    def reversed_map(self) -> dict[IncorrectLoweredAlias, CorrectWord]:
        """
        :return {
            incorrect_alias_in_lowercase_1: correct_word_1,
            incorrect_alias_in_lowercase_2: correct_word_1,
            incorrect_alias_in_lowercase_3: correct_word_2,
            ...
        }
        """
        return build_reversed_map(self.map_aliases)

    @cached_property
    def all_correct_words(self) -> list[CorrectWord]:
        """collected all correct words"""
        return sort_by_length(list(self.map_aliases.keys()))

    @cached_property
    def all_correct_words_lower(self) -> list[CorrectLoweredWord]:
        """collected all correct words in lowercase"""
        return to_lowercase(self.all_correct_words)

    @cached_property
    def incorrect_words_lower(self) -> list[IncorrectLoweredAlias]:
        """collected all incorrect words in lowercase"""
        return to_lowercase(sort_by_length(list(self.reversed_map.keys())))

    @cached_property
    def correct_words_lower(self) -> list[str]:
        """collected all correct words in lowercase"""
        return to_lowercase(sort_by_length(list(self.reversed_map.values())))
