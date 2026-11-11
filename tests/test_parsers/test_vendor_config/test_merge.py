"""Слияние уровней настроек: общий файл → поставщик → секция."""

import pytest

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


@pytest.mark.parametrize('columns', [{'3': 'price_opt'}, {}])
def test_columns_replace_as_whole(columns: dict[str, str]) -> None:
    merged = merge_config({'columns': {'0': 'title'}}, {'columns': columns})

    assert merged == {'columns': columns}


def test_merged_sections_do_not_share_mutable_settings() -> None:
    base = {'title': {'options': ['base']}, 'file_templates': ['*.xlsx']}
    override = {'title': {'extra': ['vendor']}, 'columns': {'0': 'title'}}
    first = merge_config(base, override)
    second = merge_config(base, override)

    first['title']['options'].append('changed')
    first['title']['extra'].append('changed')
    first['file_templates'].append('changed')
    first['columns']['1'] = 'rest'

    assert base == {'title': {'options': ['base']}, 'file_templates': ['*.xlsx']}
    assert override == {'title': {'extra': ['vendor']}, 'columns': {'0': 'title'}}
    assert second == {
        'title': {'options': ['base'], 'extra': ['vendor']},
        'file_templates': ['*.xlsx'],
        'columns': {'0': 'title'},
    }
