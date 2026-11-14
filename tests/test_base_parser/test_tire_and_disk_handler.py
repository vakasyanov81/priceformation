"""Рабочая реализация интерфейса группы шин и дисков."""

from unittest.mock import MagicMock

import pytest

from domain.product_group_handler import ProductGroupHandler
from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from domain.row_item.row_item import RowItem
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.row_pipeline import RowPipeline, make_row_pipeline
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.base_parser.tire_and_disk_handler import TireAndDiskHandler


def _group_handler() -> TireAndDiskHandler:
    return TireAndDiskHandler(settings=MagicMock(), stats=ParserStats())


def test_handler_keeps_title_filter_and_category_stats() -> None:
    title_filter = MagicMock()
    stats = ParserStats()

    group = TireAndDiskHandler(
        settings=MagicMock(), stats=stats, pipeline=make_row_pipeline(MagicMock(), stats, title_filter=title_filter)
    )

    assert group.pipeline.enricher.titles.title_filter is title_filter
    categories = group.pipeline.enricher.categories
    assert categories.lookup._stats is stats


def test_handler_preserves_model_for_creation_and_output() -> None:
    group_handler: ProductGroupHandler[RowItem] = _group_handler()

    position = group_handler.create_position({'title': '  Шина  ', 'price_opt': '1 500,50'})
    package = TireAndDiskResult((position,))

    assert group_handler.product_group is ProductGroup.TIRE_AND_DISK
    assert position.identity.title == 'Шина'
    assert group_handler.prepare_output(package) == ({'title': 'Шина', 'price_opt': 1500.5},)


def test_process_uses_collaborators_and_finishes_statistics() -> None:
    row_filters = MagicMock()
    row_filters.filter_warehouses.side_effect = lambda rows: rows
    enricher = MagicMock()
    enricher.keep.side_effect = lambda rows: rows
    enricher.enrich.side_effect = lambda rows: rows
    row_processor = MagicMock()
    group_handler = TireAndDiskHandler(
        settings=MagicMock(),
        pipeline=RowPipeline(StrategyHooks(pipeline=('markup',)), row_filters, enricher, row_processor),
    )
    position = group_handler.create_position(
        {
            'title': 'Шина',
            'price_opt': 100,
            'price_markup': 110,
            'rest_count': 2,
            'type_corrected': True,
            'title_conflict': True,
            'title_not_composed': True,
        }
    )

    package = group_handler.process([position])

    assert package.positions == (position,)
    assert position.pricing.percent_markup == 10
    assert position.pricing.absolute_markup == 10
    assert group_handler.stats.type_corrections == 1
    assert group_handler.stats.title_conflicts == 1
    assert group_handler.stats.titles_not_composed == 1
    row_processor.add_price_markup.assert_called_once_with(position)


def test_group_uses_tire_and_disk_grouper() -> None:
    group_handler = _group_handler()
    first = RowItem({'title': '205/55 R16 Cordiant Comfort 2'})
    second = RowItem({'title': '205/55 R16 Cordiant Comfort 2'})

    package = group_handler.group(TireAndDiskResult((first, second)))

    assert package.product_group is ProductGroup.TIRE_AND_DISK
    assert package.positions == (first, second)
    assert first.duplicate.group_by_params == second.duplicate.group_by_params
    assert (first.duplicate.order, second.duplicate.order) == ('1', '2')


def test_empty_package_keeps_group() -> None:
    group_handler = _group_handler()

    package = group_handler.group(TireAndDiskResult())

    assert package.product_group is ProductGroup.TIRE_AND_DISK
    assert package.positions == ()
    assert group_handler.prepare_output(package) == ()


def test_handler_builds_consistent_graph() -> None:
    """Фильтры и enrich используются и до pipeline, и внутри него одним экземпляром."""
    row_filters = MagicMock()
    enricher = MagicMock()
    row_filters.filter_warehouses.side_effect = lambda rows: rows
    enricher.keep.side_effect = lambda rows: rows
    enricher.enrich.side_effect = lambda rows: rows
    pipeline = RowPipeline(None, row_filters, enricher, MagicMock())
    group = TireAndDiskHandler(settings=MagicMock(), pipeline=pipeline)
    position = RowItem({'title': 'Шина', 'rest_count': 2})

    assert group.process_rows([position]) == [position]

    row_filters.filter_warehouses.assert_called_once_with([position])
    row_filters.skip_by_min_rest.assert_called_once_with(position)
    enricher.keep.assert_called_once_with([position])
    enricher.enrich.assert_called_once_with([position])
    enricher.categories.apply_category.assert_called_once_with(position)


@pytest.mark.parametrize(
    ('on_handler', 'component'),
    [
        (True, 'pipeline'),
        (False, 'row_filters'),
        (False, 'enricher'),
        (False, 'row_processor'),
        (False, 'hooks'),
    ],
)
def test_graph_rejects_independent_replacement(on_handler: bool, component: str) -> None:
    """Отдельная подмена запрещена до возникновения рассинхронизации."""
    group = _group_handler()
    target = group if on_handler else group.pipeline
    with pytest.raises(AttributeError):
        setattr(target, component, MagicMock())
