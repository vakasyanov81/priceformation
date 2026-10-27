"""ManufacturerService: когда запускается поиск производителя — без BaseParser."""

from unittest.mock import MagicMock

import pytest

from domain.row_item.row_item import RowItem
from parsers.base_parser.manufacturer_service import ManufacturerService
from parsers.base_parser.strategy_hooks import StrategyHooks

_TITLE = '205/55R16 Test'


def _service(hooks: StrategyHooks | None) -> tuple[ManufacturerService, MagicMock]:
    settings = MagicMock()
    return ManufacturerService(settings, hooks), settings.manufacturer_finder.return_value


@pytest.mark.parametrize(
    ('hooks', 'searched'),
    [
        (None, True),
        (StrategyHooks(find_manufacturer_on_enrich=True), True),
        (StrategyHooks(find_manufacturer_on_enrich=False), False),
    ],
)
def test_apply_manufacturer_follows_enrich_flag(hooks: StrategyHooks | None, searched: bool) -> None:
    service, finder = _service(hooks)

    service.apply_manufacturer(RowItem({'title': _TITLE}))

    assert finder.process.called is searched


def test_apply_after_pipeline_ignores_enrich_flag() -> None:
    service, finder = _service(StrategyHooks(find_manufacturer_on_enrich=False))
    row = RowItem({'title': _TITLE})

    service.apply_manufacturer_after_pipeline(row)

    finder.process.assert_called_once_with(row)
