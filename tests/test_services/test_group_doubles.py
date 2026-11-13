"""Команда дублей передаёт все товарные группы реальному писателю."""

import json
from contextlib import closing
from pathlib import Path
from unittest.mock import Mock

import pytest
from openpyxl import load_workbook

from domain.product_groups import ProductGroup
from infrastructure.config.fake_config_provider import FakeConfigProvider
from services.doubles_service import DoublesService
from services.parse_result import ParseResult
from services.price_report import PriceReportService
from tests.group_output_examples import group_writer
from tests.test_parsers.test_group_doubles import duplicate_packages


@pytest.fixture
def doubles_service(fake_config_provider: FakeConfigProvider) -> DoublesService:
    parsed = ParseResult()
    for package in duplicate_packages(()).values():
        parsed.add_package(package)
    reporter = PriceReportService(
        writer_factory=Mock(),
        group_writer_factory=lambda: group_writer(Path(fake_config_provider.result_folder())),
        config_provider=lambda: fake_config_provider,
    )
    return DoublesService(orchestrator=Mock(parse_all=Mock(return_value=parsed)), report_service=reporter)


def test_doubles_command_writes_both_sheets(doubles_service: DoublesService) -> None:
    report = doubles_service.make_report()
    assert report.path is not None
    assert report.files == [report.path]
    with closing(load_workbook(report.path)) as book:
        assert book.sheetnames == ['Шины и диски', 'Аккумуляторы']
        assert book['Аккумуляторы'].max_row == 3


def test_doubles_json_lists_both_streams(doubles_service: DoublesService) -> None:
    report = doubles_service.make_report(as_jsonl=True)
    assert len(report.files) == 3
    streams = [Path(path) for path in report.files if path.endswith('.jsonl')]
    assert len(streams) == 2
    assert all(path.read_text() for path in streams)
    metadata = json.loads(Path(report.files[-1]).read_text())
    groups = {schema['product_group'] for schema in metadata['files'].values()}
    assert groups == {group.value for group in ProductGroup}
