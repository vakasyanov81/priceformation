"""Реестр стратегий title: имя из конфига → фабрика."""

import pytest

from domain.exceptions import ConfigValidationError
from domain.row_item.row_item import RowItem
from parsers.strategies.normalize import NormalizeTitle
from parsers.strategies.poshk_stk_title import PoshkStkTireCompose
from parsers.strategies.title import (
    DefaultTitle,
    DiskComposeTochki,
    FillFieldsFromTitle,
    ManufacturerFromCategory,
    NormalizeSizeChunks,
    TireCompose,
    TitleWithAliases,
)
from parsers.strategies.title_markers import TitleWithMarkers
from parsers.strategies.title_params import ParamsBeforeTitle, ParamsFromTitle
from parsers.strategies.title_registry import make_title_strategy
from parsers.vendor_config.slot_configs import TitleConfig

WHERE = 'mim.json → sections[0] → title'

_KNOWN = [
    ('default', DefaultTitle),
    ('normalize_title', NormalizeTitle),
    ('normalize_size_chunks', NormalizeSizeChunks),
    ('poshk_stk_tire_compose', PoshkStkTireCompose),
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


def test_poshk_stk_tire_compose_fallback_brand_wired(monkeypatch: pytest.MonkeyPatch) -> None:
    """fallback_brand и детектор бренда доходят до сборки Пошка/STK."""
    monkeypatch.setattr(
        'parsers.strategies.title_registry.load_aliases_map',
        lambda: {'FORWARD': [], 'Алтайшина': ['АШК']},
    )
    strategy = make_title_strategy(
        TitleConfig(strategy='poshk_stk_tire_compose', fallback_brand='Алтайшина'),
        WHERE,
    )

    without_brand = strategy.prepare(RowItem({'title': 'Шина 11.00R20 И-111А 16PR 150/146K TT, шт'}))
    with_brand = strategy.prepare(RowItem({'title': 'Шина 10.00R20 FORWARD Traction-310 16PR 146/143K TT, шт'}))

    assert without_brand == 'Алтайшина 11.00R20 И-111А 16PR 150/146K TT'
    assert with_brand == '10.00R20 FORWARD Traction-310 146/143K 16PR TT'


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


def test_markers_wrap_strategy_and_set_fields() -> None:
    """markers конфига оборачивают стратегию и проставляют поля по названию."""
    strategy = make_title_strategy(
        TitleConfig(strategy='default', markers={'шип': {'season': 'зима', 'spike': 'да'}}),
        WHERE,
    )
    row = RowItem({'title': '205/55 R16 Torero MP30 шипы'})

    assert isinstance(strategy, TitleWithMarkers)
    assert strategy.prepare(row) == '205/55 R16 Torero MP30 шипы'
    assert row.tire.season == 'зима'
    assert row.tire.spike == 'да'


def test_params_from_title_wraps_strategy() -> None:
    """params_from_title оборачивает стратегию разбором параметров; без флага — нет."""
    config = TitleConfig(strategy='default', params_from_title=True)
    row = RowItem({'title': 'Диск штамп Nortec 5.5x16 6x170 ET106 d130'})

    strategy = make_title_strategy(config, WHERE)

    assert isinstance(strategy, ParamsFromTitle)
    assert strategy.prepare(row) == 'Диск штамп Nortec 5.5x16 6x170 ET106 d130'
    assert row.disk.pcd1 == 170


def test_without_markers_strategy_is_not_wrapped() -> None:
    """Без markers обёртка не создаётся."""
    strategy = make_title_strategy(TitleConfig(strategy='default'), WHERE)

    assert isinstance(strategy, DefaultTitle)


def test_params_first_wraps_before_compose() -> None:
    """params_first разбирает исходное название до сборки: обёртка ParamsBeforeTitle, не ParamsFromTitle."""
    config = TitleConfig(
        strategy='tire_compose',
        variant='four_tochki',
        params_from_title=True,
        params_first=True,
    )

    strategy = make_title_strategy(config, WHERE)

    assert isinstance(strategy, ParamsBeforeTitle)


def test_params_first_requires_params_from_title() -> None:
    config = TitleConfig(strategy='tire_compose', variant='four_tochki', params_first=True)

    with pytest.raises(ConfigValidationError, match='params_first'):
        make_title_strategy(config, WHERE)
