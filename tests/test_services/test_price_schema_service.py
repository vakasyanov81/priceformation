"""Копия file_prices до обновления и предупреждения о смене схемы прайса после."""

import logging
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import openpyxl
from log_watch import LoggerWatcher, texts_at

from domain.config_context import set_config_provider
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.group_models import BatteryConfig, BatterySection, TireAndDiskConfig
from parsers.vendor_config.models import VendorConfig
from services.price_schema_service import PriceSchemaService

_LOGGER = 'services.price_schema_service'
_VENDOR = {
    'enabled': 1,
    'code': '4',
    'name': 'Мим',
    'product_groups': [
        {
            'id': 'tire_and_disk',
            'start_row': 2,
            'file_templates': ['price*.xlsx'],
            'sections': [
                {'id': '4', 'sheet_indexes': [0], 'columns': {'0': 'code', '1': 'title'}},
            ],
        }
    ],
}


def _write_price(path: Path, header: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    book = openpyxl.Workbook()
    sheet = book.active
    assert sheet is not None
    sheet.append(header)
    sheet.append(['1', 'Шина'])
    book.save(path)


def _service(tmp_path: Path) -> PriceSchemaService:
    return PriceSchemaService(backup_folder=tmp_path / 'old')


def _run(service: PriceSchemaService) -> list[str]:
    vendor = VendorConfig.from_dict(_VENDOR, 'mim', 'mim.json')
    with patch('services.price_schema_service.load_vendor_configs', return_value={'mim': vendor}):
        return service.check()


def test_changed_header_gives_warning(
    tmp_path: Path, fake_config_provider: FakeConfigProvider, watch_logger: LoggerWatcher
) -> None:
    """смена заголовка используемой колонки после обновления — предупреждение с поставщиком и файлом."""
    price = Path(fake_config_provider.price_folder('mim')) / 'price.xlsx'
    _write_price(price, ['RN', 'Наименование'])
    service = _service(tmp_path)
    service.snapshot()
    _write_price(price, ['RN', 'Название'])
    entries = watch_logger(_LOGGER, logging.WARNING)

    warnings = _run(service)

    expected = (
        'Поставщик «Мим» (mim/price.xlsx), '
        'группа «шины + диски» (tire_and_disk): изменилась схема прайса — '
        'вкладка «Sheet», колонка B: заголовок «Наименование» → «Название» (используется как «title»)'
    )
    assert warnings == [expected]
    assert texts_at(entries(), logging.WARNING) == [expected]


def test_same_schema_no_warnings(tmp_path: Path, fake_config_provider: FakeConfigProvider) -> None:
    """схема не менялась — тишина."""
    price = Path(fake_config_provider.price_folder('mim')) / 'price.xlsx'
    _write_price(price, ['RN', 'Наименование'])
    service = _service(tmp_path)
    service.snapshot()
    _write_price(price, ['RN', 'Наименование'])

    assert _run(service) == []


def test_new_file_without_copy_is_skipped(tmp_path: Path, fake_config_provider: FakeConfigProvider) -> None:
    """файл, которого не было до обновления, сравнивать не с чем."""
    service = _service(tmp_path)
    service.snapshot()
    _write_price(Path(fake_config_provider.price_folder('mim')) / 'price.xlsx', ['RN', 'Название'])

    assert _run(service) == []


def test_unreadable_file_is_skipped(tmp_path: Path, fake_config_provider: FakeConfigProvider) -> None:
    """битый файл не роняет обновление."""
    price = Path(fake_config_provider.price_folder('mim')) / 'price.xlsx'
    _write_price(price, ['RN', 'Наименование'])
    service = _service(tmp_path)
    service.snapshot()
    price.write_text('not an excel', encoding='utf-8')

    assert _run(service) == []


def test_snapshot_uses_backup_folder_and_excludes_result(
    tmp_path: Path, fake_config_provider: FakeConfigProvider
) -> None:
    price_root = Path(fake_config_provider.price_folder('mim'))
    price_root.mkdir(parents=True)
    (price_root / 'price.xlsx').write_bytes(b'price')
    result_file = Path(fake_config_provider.result_folder()) / 'result.xlsx'
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_bytes(b'result')
    backup = tmp_path / 'custom-backup'

    assert PriceSchemaService(backup_folder=backup).snapshot() is True

    assert (backup / 'mim' / 'price.xlsx').read_bytes() == b'price'
    assert not (backup / 'result' / 'result.xlsx').exists()


def test_guard_nested_snapshots_once(tmp_path: Path, fake_config_provider: FakeConfigProvider) -> None:
    """вложенные блоки копируют и проверяют один раз — по внешнему блоку."""
    service = _service(tmp_path)
    with (
        patch.object(PriceSchemaService, 'snapshot') as snapshot,
        patch.object(PriceSchemaService, 'check') as check,
    ):
        with service.guard():
            with service.guard():
                check.assert_not_called()
            check.assert_not_called()
        snapshot.assert_called_once_with()
        check.assert_called_once_with()


def test_guard_checks_after_failure(tmp_path: Path, fake_config_provider: FakeConfigProvider) -> None:
    """сбой обновления не отменяет проверку уже скачанных файлов."""
    service = _service(tmp_path)
    with patch.object(PriceSchemaService, 'snapshot'), patch.object(PriceSchemaService, 'check') as check:
        try:
            with service.guard():
                raise RuntimeError('boom')
        except RuntimeError:
            pass
        check.assert_called_once_with()


def test_snapshot_failure_skips_check(
    tmp_path: Path, fake_config_provider: FakeConfigProvider, watch_logger: LoggerWatcher
) -> None:
    """копия не сделалась (файл занят) — предупреждение, обновление идёт, сравнения нет."""
    service = _service(tmp_path)
    entries = watch_logger(_LOGGER, logging.WARNING)
    with (
        patch('services.price_schema_service.backup_prices', side_effect=PermissionError('занято')),
        patch.object(PriceSchemaService, 'check') as check,
        service.guard(),
    ):
        updated = True

    assert updated
    check.assert_not_called()
    assert 'Не удалось сделать копию прайсов (занято)' in texts_at(entries(), logging.WARNING)[0]


def test_schema_checks_declared_battery_sheets(tmp_path: Path, fake_config_provider: FakeConfigProvider) -> None:
    """Просмотр схемы проверяет маршруты обеих групп, не требуя аккумуляторного обработчика."""
    vendor = VendorConfig.from_dict(_VENDOR, 'mim', 'mim.json')
    battery = BatterySection('battery', 'АКБ', 2, ('battery.xlsx',), sheet_indexes=(0,))
    vendor = replace(vendor, product_groups=(*vendor.product_groups, BatteryConfig((battery,))))
    root = Path(fake_config_provider.price_folder('mim'))
    _write_price(root / 'price.xlsx', ['RN', 'Наименование'])
    _write_price(root / 'battery.xlsx', ['АКБ'])
    service = _service(tmp_path)
    service.snapshot()
    _write_price(root / 'price.xlsx', ['RN', 'Название'])
    book = openpyxl.Workbook()
    sheet = book.active
    assert sheet is not None
    sheet.title = 'Аккумуляторы'
    book.save(root / 'battery.xlsx')

    with patch('services.price_schema_service.load_vendor_configs', return_value={'mim': vendor}):
        warnings = service.check()

    assert len(warnings) == 2
    assert 'tire_and_disk' in warnings[0]
    assert 'title' in warnings[0]
    assert 'batteries' in warnings[1]
    assert 'Аккумуляторы' in warnings[1]


def test_schema_check_compares_only_sheets_declared_by_section(
    tmp_path: Path, fake_config_provider: FakeConfigProvider
) -> None:
    vendor = VendorConfig.from_dict(_VENDOR, 'mim', 'mim.json')
    tire_group = vendor.product_groups[0]
    assert isinstance(tire_group, TireAndDiskConfig)
    section = replace(tire_group.sections[0], sheet_indexes=(1,))
    vendor = replace(vendor, product_groups=(replace(tire_group, sections=(section,)),))
    price = Path(fake_config_provider.price_folder('mim')) / 'price.xlsx'

    def write(second_header: str, first_header: str = 'Артикул') -> None:
        book = openpyxl.Workbook()
        first = book.active
        assert first is not None
        first.append([first_header, 'Цена'])
        second = book.create_sheet('Выбранный')
        second.append([second_header, 'Цена'])
        book.save(price)

    price.parent.mkdir(parents=True, exist_ok=True)
    write('Артикул')
    service = _service(tmp_path)
    service.snapshot()
    write('Артикул', first_header='Изменённый')

    with patch('services.price_schema_service.load_vendor_configs', return_value={'mim': vendor}):
        assert service.check() == []
        write('Название')
        warnings = service.check()

    assert len(warnings) == 1
    assert 'колонка A: заголовок «Артикул» → «Название»' in warnings[0]


def test_schema_check_uses_injected_provider_instead_of_global(tmp_path: Path) -> None:
    global_provider = FakeConfigProvider(tmp_path / 'global')
    injected = FakeConfigProvider(tmp_path / 'injected')
    set_config_provider(global_provider)
    service = PriceSchemaService(backup_folder=tmp_path / 'old', config_provider=injected)

    with patch('services.price_schema_service.load_vendor_configs', return_value={}) as load_configs:
        assert service.check() == []

    load_configs.assert_called_once_with(injected)


def test_schema_check_without_injected_provider_uses_current_global(tmp_path: Path) -> None:
    initial = FakeConfigProvider(tmp_path / 'initial')
    current = FakeConfigProvider(tmp_path / 'current')
    set_config_provider(initial)
    service = PriceSchemaService(backup_folder=tmp_path / 'old')
    set_config_provider(current)

    with patch('services.price_schema_service.load_vendor_configs', return_value={}) as load_configs:
        assert service.check() == []

    load_configs.assert_called_once_with(current)
