"""tests for alias container helpers."""

from parsers.base_parser.alias_container import AliasContainer, sort_by_length


def test_sort_by_length_longest_first() -> None:
    assert sort_by_length(["BF", "BF Goodrich"]) == ["BF Goodrich", "BF"]


def test_sort_by_length_not_lexicographic() -> None:
    assert sort_by_length(["ZZ", "AAA"]) == ["AAA", "ZZ"]


def test_reversed_map_skips_other_keys() -> None:
    container = AliasContainer(
        {
            "Alpha": ("al", "Beta", ""),
            "Beta": ("bee",),
        }
    )
    assert container.reversed_map["al"] == "Alpha"
    assert container.reversed_map["bee"] == "Beta"
    assert "beta" not in container.reversed_map


def test_reversed_map_keeps_kama_alias() -> None:
    container = AliasContainer({"НКШЗ": ("НК.ШЗ", "Кама", "Kama")})
    assert container.reversed_map["кама"] == "НКШЗ"
    assert container.reversed_map["kama"] == "НКШЗ"
