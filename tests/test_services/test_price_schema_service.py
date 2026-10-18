"""Копия file_prices до обновления и предупреждения о смене схемы прайса после."""

import logging
from pathlib import Path
from unittest.mock import patch

import openpyxl
from log_watch import LoggerWatcher, texts_at

from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.models import VendorConfig
from services.price_schema_service import PriceSchemaService

_LOGGER = 'services.price_schema_service'
_VENDOR = {
    'enabled': 1,
    'code': '4',
    'name': 'Мим',
    'start_row': 2,
    'file_templates': ['price*.xlsx'],
    'sections': [
        {'name': 'Мим', 'sheet_indexes': [0], 'columns': {'0': 'code', '1': 'title'}},
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
        'Поставщик «Мим» (mim/price.xlsx): изменилась схема прайса — '
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
