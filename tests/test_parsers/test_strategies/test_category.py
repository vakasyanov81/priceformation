"""Стратегии слота `category`: назначение `type_production` строки."""

from typing import Any

import pytest

from domain.row_item.row_item import RowItem
from parsers.strategies.category import (
    ColumnCanonicalCategory,
    FieldMapCategory,
    FixedCategory,
    HeaderRowsCategory,
    NoCategory,
    TitleKeywordsCategory,
)
from parsers.strategies.tire_category import TireSizeCategory
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


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('Камера СВК 18.4-26 ТК', 'Автокамера'),
        ('Литые диски R16 Replay', 'Диск'),
        ('130-12 об/лента', 'Ободная лента'),
        ('12.5/80-18 NEXT R-4 спецпокрышка', 'Спецшина'),
        ('16.9-28 NEXT R-4', 'Спецшина'),
        ('33х12.5-15 FORWARD Safari', 'Спецшина'),
        ('28LR26 NORTEC H-23', 'Спецшина'),
        ('10.00 R20 DOUBLEROAD унив.ось', 'Грузовая шина'),
        ('11 R22.5 TAITONG руль.ось', 'Грузовая шина'),
        ('12.00-18 К-70 ОШЗ', 'Грузовая шина'),
        ('Кама-310 16PR', 'Грузовая шина'),
        ('Nortec прицепная', 'Грузовая шина'),
        ('195/75 R16C TRIANGLE TRIN', 'Легкогрузовая шина'),
        ('265/80-16 NORTEC ET-500', 'Легкогрузовая шина'),
        ('285/75 R16LT Rapid Mud', 'Легкогрузовая шина'),
        ('185 R14C Rapid EffiVan', 'Легкогрузовая шина'),
        ('175/70 R13 Rapid P309', 'Легковая шина'),
        ('Шина 165-13 АИ-168У', 'Легковая шина'),
        ('Nortec без размера', 'Автошина'),
    ],
)
def test_tire_size_category(title: str, expected: str) -> None:
    strategy = TireSizeCategory.from_config(_config())

    assert strategy.resolve(RowItem({'title': title})) == expected


def test_tire_size_category_without_title_is_default() -> None:
    strategy = TireSizeCategory.from_config(_config())

    assert strategy.resolve(RowItem({})) == 'Автошина'
