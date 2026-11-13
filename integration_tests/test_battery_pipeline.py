"""Две реальные модели проходят штатные реестр, оркестратор, CLI и запись файлов."""

import json
from pathlib import Path

import pytest

from app.run_machine import machine_json
from cfg import init_cfg
from domain.battery.result import BatteryResult
from domain.exceptions import ConfigValidationError
from domain.product_group_result import TireAndDiskResult
from domain.product_groups import ProductGroup
from integration_tests.battery_pipeline_examples import battery_rows, supplier_environment
from parsers.registry import clear_registry
from services.parse_orchestrator import ParseOrchestrator
from services.price_report import PriceReportService
from services.service_provider import ServiceProvider

_BATTERY_COUNT = 22
_RESULT_DIR = 'file_prices/result'
_BATTERY_ID = 'batteries'
_GROUPS = 'groups'
_POSITIONS = 'positions'


@pytest.fixture
def supplier_root(tmp_path: Path) -> Path:
    """Рабочие фабрики получают образец аккумуляторов и отдельный XLSX шин."""
    init_cfg(supplier_environment(tmp_path))
    clear_registry()
    return tmp_path


def _check_battery_package(package: BatteryResult) -> None:
    assert len(package.positions) == _BATTERY_COUNT
    assert all(row.offer.sale_price == row.offer.price_recommended for row in package.positions)
    assert all(row.duplicate.group_id > 0 for row in package.positions)
    assert {row.identity.model for row in package.positions} == {'XTREME +EFB', 'XTREME Arctic'}


def _check_jsonl_metadata(folder: Path) -> None:
    metadata = json.loads((folder / 'result_meta.json').read_text())
    assert metadata['version'] == 2
    groups = {schema['product_group'] for schema in metadata['files'].values()}
    assert groups == {'tire_and_disk', _BATTERY_ID}
    assert all((folder / path).is_file() for path in metadata['files'])


class TestGroupOutputs:
    """Сквозные контракты выбранных товарных групп."""

    def test_orchestrator_keeps_real_models(self, supplier_root: Path) -> None:
        parsed = ServiceProvider.resolve(ParseOrchestrator).parse_all()
        tires = parsed.groups[ProductGroup.TIRE_AND_DISK]
        batteries = parsed.groups[ProductGroup.BATTERIES]
        assert isinstance(tires, TireAndDiskResult)
        assert isinstance(batteries, BatteryResult)
        assert len(tires.positions) == 2
        _check_battery_package(batteries)
        assert parsed.total_statistics().item_count == _BATTERY_COUNT + len(tires.positions)
        assert not list((supplier_root / _RESULT_DIR).iterdir())

    @pytest.mark.parametrize('template', [None, 'for_product_groups'])
    def test_two_groups_write_xlsx(self, supplier_root: Path, template: str | None) -> None:
        parsed = ServiceProvider.resolve(ParseOrchestrator).parse_all()
        files = ServiceProvider.resolve(PriceReportService).write_result(parsed, template=template)
        expected_files = 3 if template is None else 1
        assert len(files) == expected_files
        prices = battery_rows(files, shared=True)
        assert len(prices) == _BATTERY_COUNT
        assert all(row['Цена продажи'] == row['РРЦ'] for row in prices)
        expected_columns = {'Наценка в руб', 'Наценка в %'}
        assert all(expected_columns <= row.keys() for row in prices)
        assert isinstance(parsed.groups[ProductGroup.BATTERIES], BatteryResult)

    @pytest.mark.parametrize('template', [None, 'for_product_groups'])
    def test_json_cli_keeps_group_schemas(
        self, supplier_root: Path, template: str | None, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert machine_json('parse', all_result=True, result_template=template) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload['version'] == 2
        assert len(payload[_GROUPS][_BATTERY_ID][_POSITIONS]) == _BATTERY_COUNT
        assert len(payload[_GROUPS]['tire_and_disk'][_POSITIONS]) == 2
        row = payload[_GROUPS][_BATTERY_ID][_POSITIONS][0]
        assert row['sale_price'] == row['price_recommended']
        _check_jsonl_metadata(supplier_root / _RESULT_DIR)

    @pytest.mark.parametrize('template', ['for_batteries', 'for_product_groups'])
    def test_battery_only_cli(self, supplier_root: Path, capsys: pytest.CaptureFixture[str], template: str) -> None:
        path = supplier_root / 'parse_config/vendors/plant.json'
        raw = json.loads(path.read_text())
        raw['product_groups'].pop(0)
        path.write_text(json.dumps(raw))
        assert machine_json('parse', all_result=True, result_template=template) == 0
        payload = json.loads(capsys.readouterr().out)
        assert set(payload[_GROUPS]) == {_BATTERY_ID}
        assert len(payload[_GROUPS][_BATTERY_ID][_POSITIONS]) == _BATTERY_COUNT
        assert len(payload['files']) == 2

    def test_doubles_keeps_battery_statistics(self, supplier_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
        assert machine_json('doubles', all_result=True) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload[_GROUPS][_BATTERY_ID][_POSITIONS] == []
        assert payload[_GROUPS][_BATTERY_ID]['stats']['items'] == _BATTERY_COUNT

    def test_title_correction_stays_in_tires(self, supplier_root: Path) -> None:
        from integration_tests.battery_pipeline_examples import title_corrections

        parsed = ServiceProvider.resolve(ParseOrchestrator).parse_all()
        batteries = parsed.groups[ProductGroup.BATTERIES]
        assert isinstance(batteries, BatteryResult)
        original = batteries.positions[0].identity.title
        title_corrections(
            supplier_root / 'parse_config/correct-nomenclature.xlsx',
            [(parsed.tire_and_disk_items[0].identity.title, 'Исправленное название'), (original, 'Чужое исправление')],
        )
        ServiceProvider.resolve(PriceReportService).write_result(parsed)
        assert parsed.tire_and_disk_items[0].identity.title == 'Исправленное название'
        assert batteries.positions[0].identity.title == original


class TestGroupPreflight:
    """Сквозные контракты выбранных товарных групп."""

    def test_factory_preflight_precedes_read(self, supplier_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Неполная вторая группа отклоняется до чтения первой шинной строки."""
        from unittest.mock import Mock

        from parsers.base_parser.file_reader import FileReader

        path = supplier_root / 'parse_config/vendors/plant.json'
        raw = json.loads(path.read_text())
        raw['product_groups'][1]['columns'].pop('24')
        path.write_text(json.dumps(raw))
        reader = Mock()
        monkeypatch.setattr(FileReader, 'raw_tables', reader)
        with pytest.raises(ConfigValidationError, match=r'columns.*price_recommended'):
            ServiceProvider.resolve(ParseOrchestrator).parse_all()
        reader.assert_not_called()

    def test_disabled_groups_keep_empty_packages(self, supplier_root: Path) -> None:
        path = supplier_root / 'parse_config/vendor_activation.json'
        path.write_text('{"plant": 0}')
        parsed = ServiceProvider.resolve(ParseOrchestrator).parse_all()
        assert set(parsed.groups) == {ProductGroup.TIRE_AND_DISK, ProductGroup.BATTERIES}
        assert all(not package.positions for package in parsed.groups.values())
        assert parsed.total_statistics().item_count == 0

    def test_unsupported_template_keeps_files(self, supplier_root: Path) -> None:

        parsed = ServiceProvider.resolve(ParseOrchestrator).parse_all()
        with pytest.raises(ConfigValidationError, match='неподдерживаемые группы'):
            ServiceProvider.resolve(PriceReportService).write_result(parsed, template='for_batteries')
        assert not list((supplier_root / _RESULT_DIR).iterdir())

    def test_metadata_error_preserves_all_streams(self, supplier_root: Path) -> None:

        parsed = ServiceProvider.resolve(ParseOrchestrator).parse_all()
        folder = supplier_root / _RESULT_DIR
        metadata = folder / 'result_meta.json'
        metadata.write_text('{"version": 1}')
        with pytest.raises(ConfigValidationError, match='пересозда'):
            ServiceProvider.resolve(PriceReportService).write_result(parsed, as_jsonl=True)
        assert list(folder.iterdir()) == [metadata]
        assert json.loads(metadata.read_text()) == {'version': 1}
