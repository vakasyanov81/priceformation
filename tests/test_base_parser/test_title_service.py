"""TitleService: стратегия title или фильтр, признаки из текста поставщика — без BaseParser."""

from unittest.mock import MagicMock

from domain.row_item.row_item import RowItem
from parsers.base_parser.strategy_hooks import StrategyHooks
from parsers.base_parser.title_service import TitleService

_SOURCE = '175/65R14 Viatti Brina V-521 82T Уценка 2023г.в.'
_PREPARED = '175/65R14 Viatti Brina V-521 82T'


def test_get_prepared_title_uses_strategy_before_filter() -> None:
    strategy = MagicMock()
    strategy.prepare.return_value = _PREPARED
    title_filter = MagicMock()
    row = RowItem({'title': _SOURCE})

    prepared = TitleService(StrategyHooks(title=strategy), title_filter).get_prepared_title(row)

    assert prepared == _PREPARED
    title_filter.get_prepared_title.assert_not_called()


def test_get_prepared_title_falls_back_to_filter() -> None:
    title_filter = MagicMock()
    title_filter.get_prepared_title.return_value = 'из фильтра'
    row = RowItem({'title': _SOURCE})

    assert TitleService(StrategyHooks(), title_filter).get_prepared_title(row) == 'из фильтра'


def test_set_prepared_title_keeps_source_features_when_title_rebuilt() -> None:
    """Уценка и год берутся из текста поставщика, хотя собранное название их не несёт."""
    title_filter = MagicMock()
    title_filter.get_prepared_title.return_value = _PREPARED
    row = RowItem({'title': _SOURCE})

    reported = TitleService(None, title_filter).set_prepared_title(row)

    assert reported is False
    assert row.identity.title == _PREPARED
    assert row.stock.marked_down is True
    assert row.stock.production_year == 2023


def test_set_prepared_title_falls_back_to_source_when_empty() -> None:
    title_filter = MagicMock()
    title_filter.get_prepared_title.return_value = None
    row = RowItem({'title': _PREPARED})

    TitleService(None, title_filter).set_prepared_title(row)

    assert row.identity.title == _PREPARED


def test_is_valid_title_delegates_to_filter() -> None:
    title_filter = MagicMock()
    title_filter.is_valid_title.return_value = False

    assert TitleService(None, title_filter).is_valid_title('x') is False
    title_filter.is_valid_title.assert_called_once_with('x')
