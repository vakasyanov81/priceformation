"""Тесты сервисов: PriceReportService, DoublesService, ZapaskaService."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from domain.four_tochki import FourTochkiApiWarehouse, FourTochkiWarehouse, FourTochkiWarehouseGroup
from domain.row_item.row_item import RowItem
from infrastructure.config.fake_config_provider import FakeConfigProvider
from services.doubles_service import DoublesReport, DoublesService
from services.four_tochki_service import FourTochkiService
from services.four_tochki_service import load_remote_vendor_data as load_four_tochki_data
from services.price_report import PriceReportService
from services.zapaska_service import ZapaskaService

_TITLE = 'title'
_REPORT_PATH = 'file_prices/result/doubles.xlsx'
_NSK_API = FourTochkiApiWarehouse(id=1423, name='Новосибирск')
_API_DIRECTORY = [_NSK_API, FourTochkiApiWarehouse(id=276, name='Омск')]


def _row_item(title: str) -> RowItem:
    return RowItem({_TITLE: title})


def test_write_prices_default() -> None:
    """write_prices по умолчанию пишет xlsx и передаёт шаблон."""
    row_items = [_row_item('t1')]
    writer = MagicMock()
    writer.write_all_prices.return_value = ['file_prices/result/inner.xlsx']
    service = PriceReportService(writer_factory=lambda rows: writer)

    written = service.write_prices(row_items, template='for_drom')

    assert written == ['file_prices/result/inner.xlsx']
    writer.write_all_prices.assert_called_once_with(result_template='for_drom', as_jsonl=False)


def test_write_prices_without_template() -> None:
    """без шаблона все активные шаблоны, as_jsonl передан."""
    writer = MagicMock()
    writer.write_all_prices.return_value = []
    service = PriceReportService(writer_factory=lambda rows: writer)

    service.write_prices([], as_jsonl=True)

    writer.write_all_prices.assert_called_once_with(result_template=None, as_jsonl=True)


def test_write_doubles() -> None:
    """write_doubles вызывает writer и возвращает путь."""
    row_items = [_row_item('dup')]
    writer = MagicMock()
    writer.write_doubles_report.return_value = _REPORT_PATH
    service = PriceReportService(writer_factory=lambda rows: writer)

    path = service.write_doubles(row_items, as_jsonl=True)

    assert path == _REPORT_PATH
    writer.write_doubles_report.assert_called_once_with(as_jsonl=True)


def test_write_doubles_defaults_to_xlsx() -> None:
    """Без флага write_doubles просит xlsx (as_jsonl=False), а не jsonl."""
    row_items = [_row_item('dup')]
    writer = MagicMock()
    writer.write_doubles_report.return_value = _REPORT_PATH
    service = PriceReportService(writer_factory=lambda rows: writer)

    service.write_doubles(row_items)

    writer.write_doubles_report.assert_called_once_with(as_jsonl=False)


def test_write_doubles_factory_receives_items() -> None:
    """writer_factory для дублей получает те же записи, а не None."""
    row_items = [_row_item('dup')]
    factory = MagicMock()
    factory.return_value = MagicMock()

    PriceReportService(writer_factory=factory).write_doubles(row_items)

    factory.assert_called_once_with(row_items)


def test_make_report_defaults_to_xlsx() -> None:
    """Без флага make_report просит xlsx (as_jsonl=False), а не jsonl."""
    parsed = MagicMock()
    parsed.parsed_items = []
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = parsed
    reporter = MagicMock()
    reporter.write_doubles.return_value = _REPORT_PATH
    service = DoublesService(orchestrator=orchestrator, report_service=reporter)

    service.make_report()

    reporter.write_doubles.assert_called_once_with([], as_jsonl=False)


def test_writer_factory_receives_items() -> None:
    """writer_factory создаёт writer для тех же записей."""
    row_items = [_row_item('t1')]
    factory = MagicMock()
    writer = MagicMock()
    factory.return_value = writer
    service = PriceReportService(writer_factory=factory)

    service.write_prices(row_items)

    factory.assert_called_once_with(row_items)


def test_make_report_filters_doubles() -> None:
    """make_report парсит, фильтрует дубли и пишет отчёт."""
    double_row = _row_item('dup')
    double_row.set_field('is_double', True)
    candidate = _row_item('cand')
    candidate.set_field('double_candidate', True)
    unique = _row_item('uniq')
    parsed = MagicMock()
    parsed.parsed_items = [double_row, candidate, unique]
    orchestrator = MagicMock()
    orchestrator.parse_all.return_value = parsed
    reporter = MagicMock()
    reporter.write_doubles.return_value = _REPORT_PATH
    service = DoublesService(orchestrator=orchestrator, report_service=reporter)

    report = service.make_report(as_jsonl=True)

    assert isinstance(report, DoublesReport)
    assert report.parse_result is parsed
    assert report.doubles == [double_row, candidate]
    assert report.path == _REPORT_PATH
    orchestrator.parse_all.assert_called_once_with()
    reporter.write_doubles.assert_called_once_with(parsed.parsed_items, as_jsonl=True)


def test_upload_zapaska_data() -> None:
    """upload_data вызывает загрузку удалённых данных с API-конфигом."""
    api = MagicMock()
    with (
        patch('services.vendor_activity.load_vendor_configs', return_value={}),
        patch('services.zapaska_service.get_zapaska_api_config', return_value=api),
        patch('services.zapaska_service.load_remote_vendor_data') as mock_load,
    ):
        ZapaskaService().upload_data()
    mock_load.assert_called_once_with(api=api)


def test_upload_four_tochki_data() -> None:
    """upload_data вызывает загрузку данных Форточек с API-конфигом."""
    api = MagicMock()
    groups = (MagicMock(),)
    with (
        patch('services.vendor_activity.load_vendor_configs', return_value={}),
        patch('services.four_tochki_service.get_four_tochki_api_config', return_value=api),
        patch('services.four_tochki_service.load_four_tochki_warehouse_groups', return_value=groups),
        patch('services.four_tochki_service.load_remote_vendor_data') as mock_load,
    ):
        FourTochkiService().upload_data()
    mock_load.assert_called_once_with(api=api, groups=groups)


def test_four_tochki_load_selects_warehouses_and_downloads_to_price_folder(
    fake_config_provider: FakeConfigProvider,
) -> None:
    """Склады подбираются по группам из справочника; каталоги качаются только по ним — в папку прайсов Форточек."""
    api = MagicMock()
    groups = (FourTochkiWarehouseGroup(name='novosibirsk', keywords=('Новосибирск',), merge=True),)
    with (
        patch('services.four_tochki_service.fetch_warehouses', return_value=_API_DIRECTORY),
        patch('services.four_tochki_service.download_catalogs') as mock_download,
    ):
        load_four_tochki_data(api=api, groups=groups)

    mock_download.assert_called_once_with(
        dest_dir=Path(fake_config_provider.price_folder('four_tochki')),
        api=api,
        warehouses=(FourTochkiWarehouse(id=1423, name='Новосибирск', group='novosibirsk', merge_group='novosibirsk'),),
    )
