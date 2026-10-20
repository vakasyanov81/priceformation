"""Обёртка `params_from_title`: параметры шин и дисков из названия в поля позиции."""

import logging

from log_watch import LoggerWatcher, texts_at

from domain.row_item.row_item import RowItem
from infrastructure.logging.console import FILE_ONLY
from parsers.strategies.poshk_stk_title import PoshkStkTireCompose
from parsers.strategies.title import DefaultTitle, DiskComposeTochki, ManufacturerFromCategory, TireCompose
from parsers.strategies.title_conflicts import title_conflicts_message
from parsers.strategies.title_params import ParamsBeforeTitle, ParamsFromTitle

_PIONER = '215/75R17.5 Triangle TR685 135/133L 16PR TL рулевая'


def test_fills_disk_fields_and_keeps_title() -> None:
    raw = 'Диск штамп Nortec-16 11.75x22.5 10x335 ET0 d281'
    row = RowItem({'title': raw})

    assert ParamsFromTitle(DefaultTitle()).prepare(row) == raw
    assert row.disk.pcd1 == 335
    assert row.disk.eet == 0


def test_fills_tire_fields_for_pioner() -> None:
    row = RowItem({'title': _PIONER, 'price_opt': 1000})

    strategy = ParamsFromTitle(ManufacturerFromCategory(lambda: 'Triangle'))

    assert strategy.prepare(row) == _PIONER
    assert (row.tire.width, row.tire.height_percent) == ('215', '75')
    assert row.tire.diameter == '17.5'
    assert (row.tire.index_load, row.tire.index_velocity) == ('135/133', 'L')
    assert (row.tire.layering, row.tire.intimacy) == ('16PR', 'TL')
    assert row.identity.model == 'TR685'


def test_parses_title_after_manufacturer_is_prepended() -> None:
    """Производитель раздела вставлен в название до разбора: модель не принимает его за бренд."""
    row = RowItem({'title': '215/75R17.5 TR685 135/133L', 'price_opt': 1000})

    ParamsFromTitle(ManufacturerFromCategory(lambda: 'Triangle')).prepare(row)

    assert row.identity.model == 'TR685'


def test_fills_tire_fields_from_poshk_compose() -> None:
    row = RowItem({'title': 'Автошина 235/75R17,5 LingLong LLA78 18PR 143/141J TL трал'})

    ParamsFromTitle(PoshkStkTireCompose('', None)).prepare(row)

    assert (row.tire.width, row.tire.height_percent) == ('235', '75')
    assert row.identity.model == 'LLA78'


def test_fills_without_price() -> None:
    row = RowItem({'title': _PIONER})

    ParamsFromTitle(ManufacturerFromCategory(lambda: 'Triangle')).prepare(row)

    assert row.tire.width == '215'


def test_keeps_existing_values() -> None:
    row = RowItem({'title': _PIONER, 'width': '999'})

    ParamsFromTitle(DefaultTitle()).prepare(row)

    assert row.tire.width == '999'


def test_ignores_unparsable_title() -> None:
    row = RowItem({'title': 'Камера УК-14М ОШЗ'})

    assert ParamsFromTitle(DefaultTitle()).prepare(row) == 'Камера УК-14М ОШЗ'
    assert row.tire.width is None


def test_fills_tube_size_and_keeps_title() -> None:
    row = RowItem({'title': 'Камера СВК 20.5-25 ГК-260 (0)'})

    assert ParamsFromTitle(DefaultTitle()).prepare(row) == 'Камера СВК 20.5-25 ГК-260 (0)'
    assert (row.tire.width, row.tire.diameter) == ('20.5', '25')


def test_keeps_none_title() -> None:
    assert ParamsFromTitle(DefaultTitle()).prepare(RowItem({})) is None


_KHOMEN = '15 Khomen KHW1501 ZV Vesta/Almera 6.0*15 4*100 ET50 D60.1 GRAY'
_PARAMS_LOGGER = 'parsers.strategies.title_conflicts'


def test_title_et_overrides_column_and_is_logged(watch_logger: LoggerWatcher) -> None:
    """Колонка ET=40 при ET50 в названии: берём название и пишем расхождение в лог."""
    entries = watch_logger(_PARAMS_LOGGER, logging.WARNING)
    row = RowItem({'title': _KHOMEN, 'eet': 40})

    ParamsFromTitle(DefaultTitle()).prepare(row)

    assert row.disk.eet == 50
    messages = texts_at(entries(), logging.WARNING)
    assert len(messages) == 1
    assert row.vendor.title_conflict is True
    assert 'eet 40' in messages[0]
    assert '50' in messages[0]
    assert _KHOMEN in messages[0]


def test_tire_index_conflict_is_logged(watch_logger: LoggerWatcher) -> None:
    """Колонка speed_index=H при 86T в названии: индексы берём из названия и пишем в лог."""
    entries = watch_logger(_PARAMS_LOGGER, logging.WARNING)
    row = RowItem({'title': '185/65R14 Hankook Kinergy Eco 2 K435 86T', 'index_load': '86', 'index_velocity': 'H'})

    ParamsFromTitle(DefaultTitle()).prepare(row)

    assert (row.tire.index_load, row.tire.index_velocity) == ('86', 'T')
    messages = texts_at(entries(), logging.WARNING)
    assert len(messages) == 1
    assert 'index_velocity' in messages[0]


def test_same_value_in_column_and_title_is_not_logged(watch_logger: LoggerWatcher) -> None:
    """40 в колонке и ET40 в названии (число и строка) — не расхождение."""
    entries = watch_logger(_PARAMS_LOGGER, logging.WARNING)
    row = RowItem({'title': _KHOMEN.replace('ET50', 'ET40'), 'eet': 40})

    ParamsFromTitle(DefaultTitle()).prepare(row)

    assert texts_at(entries(), logging.WARNING) == []


def test_empty_column_is_filled_without_log(watch_logger: LoggerWatcher) -> None:
    """Колонки нет — вылет берём из названия, расхождения нет."""
    entries = watch_logger(_PARAMS_LOGGER, logging.WARNING)
    row = RowItem({'title': _KHOMEN})

    ParamsFromTitle(DefaultTitle()).prepare(row)

    assert row.disk.eet == 50
    assert texts_at(entries(), logging.WARNING) == []


def test_before_title_composes_tire_from_raw_title() -> None:
    """Поля берутся из исходного названия до сборки; бренд и модель — из колонок прайса."""
    row = RowItem(
        {
            'title': '205/65R16 95T Brina Nordico V-522 TL (102 шип.)',
            'manufacturer_name': 'Viatti',
            'model': 'Brina Nordico V-522',
            'tire_type': 'Легковая',
        }
    )

    title = ParamsBeforeTitle(TireCompose('four_tochki')).prepare(row)

    assert title == '205/65R16 Viatti Brina Nordico V-522 95T'
    assert (row.tire.width, row.tire.diameter) == ('205', '16')


def test_before_title_parses_disk_without_disk_prefix() -> None:
    """У диска API слова «Диск» нет: разбор с крепежом, название собирается по колонкам."""
    row = RowItem(
        {
            'title': '7x17/5x108 ET50 D63,35 Онтарио (КЛ216) Алмаз',
            'manufacturer_name': 'Khomen',
            'model': 'Онтарио (КЛ216)',
            'color': 'Алмаз',
        }
    )

    title = ParamsBeforeTitle(DiskComposeTochki()).prepare(row)

    assert title == '7.0x17 5x108 ET50 63.35 Алмаз Khomen Онтарио (КЛ216)'
    assert (row.disk.slot_count, row.disk.pcd1) == (5, 108)
    assert row.disk.eet == 50


def test_params_from_title_keeps_bare_disk_out() -> None:
    """Без params_first название без слова «Диск» не разбирается: прежнее поведение для других поставщиков."""
    row = RowItem({'title': '7x17/5x108 ET50 D63,35 Онтарио (КЛ216) Алмаз'})

    ParamsFromTitle(DefaultTitle()).prepare(row)

    assert row.disk.pcd1 is None


def test_before_title_conflict_log_names_source_title(watch_logger: LoggerWatcher) -> None:
    """Расхождение колонки и названия при params_first: в логе исходное название, а не пустота."""
    entries = watch_logger(_PARAMS_LOGGER, logging.WARNING)
    row = RowItem({'title': _KHOMEN, 'eet': 40})

    ParamsBeforeTitle(DefaultTitle()).prepare(row)

    messages = texts_at(entries(), logging.WARNING)
    assert len(messages) == 1
    assert messages[0].endswith(f'// {_KHOMEN}')


class _Collector(logging.Handler):
    """Складывает записи лога в список."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_conflict_is_file_only() -> None:
    """Подробное расхождение уходит только в файл лога, на экран — только сводка."""
    collector = _Collector()
    logger = logging.getLogger(_PARAMS_LOGGER)
    logger.addHandler(collector)
    try:
        ParamsFromTitle(DefaultTitle()).prepare(RowItem({'title': _KHOMEN, 'eet': 40}))
    finally:
        logger.removeHandler(collector)

    assert [getattr(record, FILE_ONLY, False) for record in collector.records] == [True]


def test_no_conflict_does_not_mark_row() -> None:
    row = RowItem({'title': _KHOMEN})

    ParamsFromTitle(DefaultTitle()).prepare(row)

    assert not row.vendor.title_conflict


def test_title_conflicts_message() -> None:
    assert title_conflicts_message(0) == ''
    assert '3' in title_conflicts_message(3)
