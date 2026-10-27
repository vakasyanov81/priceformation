"""RowPipeline: порядок шагов разбора строки на заглушках коллабораторов — без BaseParser."""

from typing import NamedTuple
from unittest.mock import MagicMock

from domain.row_item.row_item import RowItem
from parsers.base_parser.row_pipeline import RowPipeline
from parsers.base_parser.strategy_hooks import StrategyHooks


class _Setup(NamedTuple):
    pipeline: RowPipeline
    calls: MagicMock


def _setup(hooks: StrategyHooks | None) -> _Setup:
    """Все коллабораторы пишут вызовы в общий `calls`, чтобы проверять порядок."""
    calls = MagicMock()
    row_filters = calls.row_filters
    enricher = MagicMock()
    enricher.titles = calls.titles
    enricher.categories = calls.categories
    enricher.manufacturers = calls.manufacturers
    return _Setup(RowPipeline(hooks, row_filters, enricher, calls.row_processor), calls)


def _names(calls: MagicMock) -> list[str]:
    return [call[0] for call in calls.mock_calls]


def test_default_order_without_hooks() -> None:
    setup = _setup(None)

    setup.pipeline.process_row(RowItem({}))

    assert _names(setup.calls) == [
        'row_filters.skip_by_min_rest',
        'categories.apply_category',
        'categories.zero_rest_without_category',
        'categories.apply_category_fields',
        'row_processor.add_price_markup',
    ]


def test_hooks_pipeline_order_between_warehouse_order_and_final_manufacturer() -> None:
    setup = _setup(StrategyHooks(pipeline=('markup', 'title')))

    setup.pipeline.process_row(RowItem({}))

    assert _names(setup.calls) == [
        'row_filters.apply_warehouse_order',
        'row_processor.add_price_markup',
        'titles.set_prepared_title',
        'manufacturers.apply_manufacturer_after_pipeline',
    ]


def test_unknown_step_is_skipped() -> None:
    setup = _setup(StrategyHooks(pipeline=('nope', 'min_rest')))

    setup.pipeline.process_row(RowItem({}))

    assert 'row_filters.skip_by_min_rest' in _names(setup.calls)
    assert len(_names(setup.calls)) == 3


def test_run_processes_every_row() -> None:
    setup = _setup(StrategyHooks(pipeline=('min_rest',)))
    rows = [RowItem({}), RowItem({})]

    setup.pipeline.run(rows)

    assert setup.calls.row_filters.skip_by_min_rest.call_count == len(rows)
