"""Реестр стратегий title: имя из конфига → фабрика."""

import pytest

from domain.exceptions import ConfigValidationError
from domain.row_item.row_item import RowItem
from parsers.strategies.normalize import NormalizeTitle
from parsers.strategies.stk_title import StkTireCompose
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
    ('stk_tire_compose', StkTireCompose),
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


def test_normalize_size_chunks_fallback_brand_wired(monkeypatch: pytest.MonkeyPatch) -> None:
    """fallback_brand конфига подменяет ведущую «Шина», когда бренда в title нет."""
    monkeypatch.setattr(
        'parsers.strategies.title_registry.load_aliases_map',
        lambda: {'Nortec': [], 'Алтайшина': ['АШК']},
    )
    strategy = make_title_strategy(
        TitleConfig(strategy='normalize_size_chunks', fallback_brand='Алтайшина'),
        WHERE,
    )

    assert strategy.prepare(RowItem({'title': 'Шина 155/65R13'})) == 'Алтайшина 155/65R13'
    assert strategy.prepare(RowItem({'title': 'Шина Nortec'})) == 'Nortec'


def test_normalize_size_chunks_without_fallback_does_not_read_aliases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Без fallback_brand алиасы производителей не читаются."""
    monkeypatch.setattr(
        'parsers.strategies.title_registry.load_aliases_map',
        lambda: pytest.fail('aliases must not be loaded'),
    )
    strategy = make_title_strategy(TitleConfig(strategy='normalize_size_chunks'), WHERE)

    assert strategy.prepare(RowItem({'title': 'Шина 155/65R13'})) == '155/65R13'


def test_unknown_strategy_raises_with_location() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестная стратегия title') as exc_info:
        make_title_strategy(TitleConfig(strategy='nope'), WHERE)

    assert WHERE in str(exc_info.value)


def test_unknown_tire_variant_raises() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестный вариант') as exc_info:
        make_title_strategy(TitleConfig(strategy='tire_compose', variant='nope'), WHERE)

    assert WHERE in str(exc_info.value)


def test_unknown_disk_variant_raises() -> None:
    with pytest.raises(ConfigValidationError, match='неизвестный вариант') as exc_info:
        make_title_strategy(TitleConfig(strategy='disk_compose', variant='nope'), WHERE)

    assert WHERE in str(exc_info.value)


def test_aliases_wraps_strategy(monkeypatch: pytest.MonkeyPatch) -> None:
    """Обёртка aliases читает таблицу поставщика и применяет её к title."""
    seen: dict[str, str] = {}

    def _aliases(supplier_name: str) -> dict[str, str]:
        seen['supplier_name'] = supplier_name
        return {'Старый': 'Новый'}

    monkeypatch.setattr('parsers.strategies.title_registry.load_title_aliases', _aliases)
    strategy = make_title_strategy(TitleConfig(strategy='default', aliases=True), WHERE, supplier_name='s')

    assert isinstance(strategy, TitleWithAliases)
    assert strategy.prepare(RowItem({'title': 'Старый'})) == 'Новый'
    assert seen['supplier_name'] == 's'
