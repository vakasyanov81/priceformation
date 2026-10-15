"""Выбор главного дубля: обычный товар, свежая партия, цена."""

from typing import Any

from domain.row_item.row_item import RowItem
from parsers.common_price_main_double import main_double


def _row(price: int, **fields: Any) -> RowItem:
    return RowItem({'title': 'шина', 'price_markup': price, **fields})


def test_cheapest_wins_among_equal_rows() -> None:
    cheap, dear = _row(10), _row(20)
    assert main_double([dear, cheap]) is cheap


def test_fresh_row_beats_cheaper_old_batch() -> None:
    """Старая партия дешевле, но главный — более свежая позиция."""
    old = _row(10, production_year=2022)
    new = _row(20, production_year=2023)
    assert main_double([old, new]) is new


def test_row_without_year_counts_as_fresh() -> None:
    """Год пишут только у старых партий: позиция без года свежее любой с годом."""
    old = _row(10, production_year=2023)
    undated = _row(20)
    assert main_double([old, undated]) is undated


def test_cheapest_within_freshest_batch() -> None:
    old = _row(5, production_year=2021)
    fresh_dear = _row(30, production_year=2023)
    fresh_cheap = _row(20, production_year=2023)
    assert main_double([old, fresh_dear, fresh_cheap]) is fresh_cheap


def test_older_than_marker_loses_to_explicit_year() -> None:
    """«2 года и старше» старее любого явного года."""
    oldest = _row(10, production_year=1)
    dated = _row(20, production_year=2022)
    assert main_double([oldest, dated]) is dated


def test_markdown_is_not_main_while_regular_exists() -> None:
    markdown = _row(10, marked_down=True)
    regular = _row(20, production_year=2021)
    assert main_double([markdown, regular]) is regular


def test_all_markdown_still_has_main() -> None:
    cheap = _row(10, marked_down=True)
    dear = _row(20, marked_down=True)
    assert main_double([dear, cheap]) is cheap
