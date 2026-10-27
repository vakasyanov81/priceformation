"""CategoryService: категория, независимый тип, поля по размеру — без BaseParser."""

from unittest.mock import MagicMock

from domain.row_item.row_item import RowItem
from parsers.base_parser.category_service import CategoryLookup, CategoryService
from parsers.base_parser.parse_statistic import ParserStats
from parsers.base_parser.strategy_hooks import StrategyHooks

_TITLE = '205/55R16 Test'
_DECLARED = 'Грузовая шина'
_OWN = 'Легковая шина'


def _service(hooks: StrategyHooks | None = None) -> tuple[CategoryService, ParserStats]:
    stats = ParserStats()
    return CategoryService(hooks, CategoryLookup(stats)), stats


def test_category_for_passes_lookup_as_context() -> None:
    strategy = MagicMock()
    strategy.resolve.return_value = _DECLARED
    service, _stats = _service(StrategyHooks(category=strategy))
    row = RowItem({'title': _TITLE})

    assert service.category_for(row) == _DECLARED
    strategy.resolve.assert_called_once_with(row, service.lookup)


def test_record_unknown_category_goes_to_stats() -> None:
    stats = ParserStats()

    CategoryLookup(stats).record_unknown_category('SUV')

    assert stats.unknown_category_skips == ['SUV']


def test_find_canonical_category_works_without_reset() -> None:
    assert CategoryLookup(ParserStats()).find_canonical_category(None) is None


def test_correction_category_is_noop_before_reset() -> None:
    row = RowItem({'title': _TITLE, 'type_production': 'грузовая'})

    CategoryLookup(ParserStats()).correction_category(row)

    assert row.vendor.type_production == 'грузовая'


def test_apply_category_without_product_type_sets_declared() -> None:
    strategy = MagicMock()
    strategy.resolve.return_value = _DECLARED
    service, _stats = _service(StrategyHooks(category=strategy))
    row = RowItem({'title': _TITLE})

    service.apply_category(row)

    assert row.vendor.type_production == _DECLARED
    assert row.vendor.type_corrected is None


def test_apply_category_prefers_own_type_and_marks_correction() -> None:
    strategy = MagicMock()
    strategy.resolve.return_value = _DECLARED
    product_type = MagicMock()
    product_type.classify.return_value = _OWN
    service, _stats = _service(StrategyHooks(category=strategy, product_type=product_type))
    row = RowItem({'title': _TITLE})

    service.apply_category(row)

    assert row.vendor.type_production == _OWN
    assert row.vendor.type_corrected is True


def test_apply_category_keeps_declared_when_own_type_unknown() -> None:
    strategy = MagicMock()
    strategy.resolve.return_value = _DECLARED
    product_type = MagicMock()
    product_type.classify.return_value = ''
    service, _stats = _service(StrategyHooks(category=strategy, product_type=product_type))
    row = RowItem({'title': _TITLE})

    service.apply_category(row)

    assert row.vendor.type_production == _DECLARED
    assert row.vendor.type_corrected is False


def test_zero_rest_without_category_only_when_flag_and_no_type() -> None:
    service, _stats = _service(StrategyHooks(zero_rest_without_category=True))
    without = RowItem({'title': _TITLE, 'rest_count': 5})
    typed = RowItem({'title': _TITLE, 'rest_count': 5, 'type_production': _OWN})

    service.zero_rest_without_category(without)
    service.zero_rest_without_category(typed)

    assert (without.stock.rest_count, typed.stock.rest_count) == (0, 5)


def test_zero_rest_without_category_is_off_without_hooks() -> None:
    row = RowItem({'title': _TITLE, 'rest_count': 5})

    _service()[0].zero_rest_without_category(row)

    assert row.stock.rest_count == 5


def test_apply_category_fields_delegates_to_strategy() -> None:
    fields = MagicMock()
    service, _stats = _service(StrategyHooks(category_fields=fields))
    row = RowItem({'title': _TITLE})

    service.apply_category_fields(row)
    _service()[0].apply_category_fields(row)

    fields.apply.assert_called_once_with(row)
