"""Слияние уровней настроек: общий файл → поставщик → секция."""

from parsers.vendor_config.merge import merge_config


def test_objects_merge_by_keys_and_values_replace() -> None:
    base = {'title': {'strategy': 'a', 'variant': 'v'}, 'min_rest': 4, 'templates': ['x']}
    override = {'title': {'strategy': 'b'}, 'min_rest': 0, 'templates': ['y']}

    assert merge_config(base, override) == {
        'title': {'strategy': 'b', 'variant': 'v'},
        'min_rest': 0,
        'templates': ['y'],
    }


def test_markup_rules_replace_as_whole() -> None:
    base = {'rules': {'markup_rules': {'low': 1}, 'floor': 5}}
    override = {'rules': {'markup_rules': {'high': 2}}}

    merged_rules = merge_config(base, override)['rules']

    assert merged_rules == {'markup_rules': {'high': 2}, 'floor': 5}


def test_sources_are_not_mutated() -> None:
    base = {'title': {'strategy': 'a'}}
    merge_config(base, {'title': {'variant': 'v'}})

    assert base == {'title': {'strategy': 'a'}}
