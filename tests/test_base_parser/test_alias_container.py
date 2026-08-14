"""tests for alias container helpers."""

from parsers.base_parser.alias_container import sort_by_length


def test_sort_by_length_longest_first() -> None:
    assert sort_by_length(["BF", "BF Goodrich"]) == ["BF Goodrich", "BF"]
