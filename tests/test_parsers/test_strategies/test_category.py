"""Стратегии слота `category`: назначение `type_production` строки."""

from typing import Any

from domain.row_item.row_item import RowItem
from parsers.strategies.category import (
    ColumnCanonicalCategory,
    FieldMapCategory,
    FixedCategory,
    HeaderRowsCategory,
    NoCategory,
    TitleKeywordsCategory,
)
from parsers.vendor_config.slot_configs import CategoryConfig


class _FakeContext:
    """Дуб-контекст: фиксирует сработавшие пропуски и отдаёт готовый ответ."""

    def __init__(self, resolved: str | None = None) -> None:
        self._resolved = resolved
        self.skips: list[str] = []

    def find_canonical_category(self, raw_type: str | None) -> str | None:
        return self._resolved

    def record_unknown_category(self, raw_label: str) -> None:
        self.skips.append(raw_label)


def _config(**overrides: Any) -> CategoryConfig:
    return CategoryConfig(**overrides)


def test_no_category_returns_none() -> None:
    strategy = NoCategory.from_config(_config())

    assert strategy.resolve(RowItem({'title': 'Шина'})) is None


def test_fixed_category_returns_value() -> None:
    strategy = FixedCategory.from_config(_config(fixed_value='Диск'))

    assert strategy.resolve(RowItem({})) == 'Диск'


def test_title_keywords_matches_first_in_order() -> None:
    strategy = TitleKeywordsCategory.from_config(
        _config(mapping={'ободная лента': 'Ободная лента', 'шина': 'Автошина'}),
    )

    assert strategy.resolve(RowItem({'title': 'Шина ободная лента'})) == 'Ободная лента'


def test_title_keywords_falls_back_to_default() -> None:
    strategy = TitleKeywordsCategory.from_config(
        _config(mapping={'камера': 'Автокамера'}, default_value='Разное'),
    )

    assert strategy.resolve(RowItem({'title': 'Болты'})) == 'Разное'


def test_title_keywords_is_case_insensitive() -> None:
    strategy = TitleKeywordsCategory.from_config(_config(mapping={'диск': 'Диск'}))

    assert strategy.resolve(RowItem({'title': 'ЛИТОЙ ДИСК R16'})) == 'Диск'


def test_field_map_reads_normalized_field() -> None:
    strategy = FieldMapCategory.from_config(
        _config(field_name='tire_type', mapping={'грузовая': 'Грузовая шина'}, default_value='Автошина'),
    )

    assert strategy.resolve(RowItem({'tire_type': '  Грузовая '})) == 'Грузовая шина'


def test_field_map_falls_back_to_default() -> None:
    strategy = FieldMapCategory.from_config(
        _config(field_name='tire_type', mapping={'грузовая': 'Грузовая шина'}, default_value='Автошина'),
    )

    assert strategy.resolve(RowItem({})) == 'Автошина'


def test_column_canonical_uses_context() -> None:
    strategy = ColumnCanonicalCategory.from_config(_config(unknown_skip=True))
    context = _FakeContext(resolved='Грузовая шина')

    assert strategy.resolve(RowItem({'type_production': 'Грузовая'}), context) == 'Грузовая шина'


def test_column_canonical_records_unknown_when_requested() -> None:
    strategy = ColumnCanonicalCategory.from_config(_config(unknown_skip=True))
    context = _FakeContext()

    assert strategy.resolve(RowItem({'type_production': 'Марсианская'}), context) == ''
    assert context.skips == ['Марсианская']


def test_column_canonical_ignores_unknown_without_flag() -> None:
    strategy = ColumnCanonicalCategory.from_config(_config(unknown_skip=False))
    context = _FakeContext()

    assert strategy.resolve(RowItem({'type_production': 'Марсианская'}), context) == ''
    assert context.skips == []


def test_column_canonical_without_context_uses_default_finder() -> None:
    strategy = ColumnCanonicalCategory.from_config(_config())

    assert strategy.resolve(RowItem({'type_production': 'Грузовая'})) == 'Грузовая шина'


def test_header_rows_updates_state_on_category_row() -> None:
    strategy = HeaderRowsCategory()

    assert strategy.resolve(RowItem({'title': 'автошины TRIANGLE'})) == 'автошины'
    assert strategy.resolve(RowItem({'title': 'Tigar', 'price_opt': 1200})) == 'автошины'


def test_header_rows_splits_slash_and_space() -> None:
    strategy = HeaderRowsCategory()

    assert strategy.resolve(RowItem({'title': 'диски r16/шины'})) == 'диски'


def test_header_rows_zero_rest_flag() -> None:
    strategy = HeaderRowsCategory.from_config(_config(zero_rest_categories=('прочие',)))
    strategy.resolve(RowItem({'title': 'прочие товары'}))

    assert strategy.is_zero_rest_category() is True

    strategy.resolve(RowItem({'title': 'автошины'}))
    assert strategy.is_zero_rest_category() is False
