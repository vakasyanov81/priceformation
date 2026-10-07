"""Реестр стратегий title: имя из конфига → фабрика."""

import pytest

from domain.exceptions import ConfigValidationError
from parsers.strategies.normalize import NormalizeTitle
from parsers.strategies.title import (
    DefaultTitle,
    DiskComposeTochki,
    FillFieldsFromTitle,
    ManufacturerFromCategory,
    NormalizeSizeChunks,
    TireCompose,
    TitleWithAliases,
)
from parsers.strategies.title_registry import make_title_strategy
from parsers.vendor_config.slot_configs import TitleConfig

WHERE = 'mim.json → sections[0] → title'

_KNOWN = [
    ('default', DefaultTitle),
    ('normalize_title', NormalizeTitle),
    ('normalize_size_chunks', NormalizeSizeChunks),
    ('fill_fields_from_title', FillFieldsFromTitle),
]


@pytest.mark.parametrize(('name', 'expected_type'), _KNOWN)
def test_make_known_title_strategy(name: str, expected_type: type) -> None:
    strategy = make_title_strategy(TitleConfig(strategy=name), WHERE)

    assert isinstance(strategy, expected_type)


def test_tire_compose_built_by_variant() -> None:
    strategy = make_title_strategy(TitleConfig(strategy='tire_compose', variant='mim_simple'), WHERE)

    assert isinstance(strategy, TireCompose)


def test_disk_compose_built_by_variant() -> None:
    strategy = make_title_strategy(TitleConfig(strategy='disk_compose', variant='four_tochki'), WHERE)

    assert isinstance(strategy, DiskComposeTochki)


def test_manufacturer_from_category_built() -> None:
    strategy = make_title_strategy(TitleConfig(strategy='manufacturer_from_category'), WHERE)

    assert isinstance(strategy, ManufacturerFromCategory)


def test_unknown_strategy_raises_with_location() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестная стратегия title'):
        make_title_strategy(TitleConfig(strategy='nope'), WHERE)


def test_unknown_tire_variant_raises() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестный вариант'):
        make_title_strategy(TitleConfig(strategy='tire_compose', variant='nope'), WHERE)


def test_unknown_disk_variant_raises() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестный вариант'):
        make_title_strategy(TitleConfig(strategy='disk_compose', variant='nope'), WHERE)


def test_aliases_wraps_strategy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('parsers.strategies.title_registry.load_title_aliases', lambda _name: {'A': 'B'})
    strategy = make_title_strategy(TitleConfig(strategy='default', aliases=True), WHERE, supplier_name='s')

    assert isinstance(strategy, TitleWithAliases)
