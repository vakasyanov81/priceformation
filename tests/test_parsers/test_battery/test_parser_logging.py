"""Итоговый лог аккумуляторной секции через настоящий парсер и обработчик."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser.base_parser_config import ParseParamsSupplier, ParserParams, make_parse_config
from parsers.base_parser.price_files import PriceFiles
from parsers.base_parser.routing import VendorRouting
from parsers.battery.handler import BatteryHandler
from parsers.battery.parser import BatteryParser
from parsers.vendor_config.battery_settings import BatterySettings
from parsers.vendor_config.group_models import BatteryConfig
from parsers.vendor_config.models import VendorConfig


def _parser() -> BatteryParser:
    parser_params = ParserParams(
        supplier=ParseParamsSupplier('plant', 'План-Т', 'plant_batteries'),
        start_row=1,
        sheet_info='',
        columns={},
        stop_words=(),
        file_templates=('*.xls',),
        sheet_indexes=(),
    )
    config = make_parse_config(parser_params, config_provider=MagicMock())
    return BatteryParser(config, BatteryHandler(BatterySettings(), 'План-Т'))


def test_battery_parser_logs_count_markup_and_finish(caplog: pytest.LogCaptureFixture) -> None:
    rows = [
        {'code': '001', 'title': 'XTREME +EFB 60', 'rest_count': 1, 'price_opt': 100, 'price_recommended': 125},
        {'code': '002', 'title': 'XTREME Arctic 60', 'rest_count': 2, 'price_opt': 200, 'price_recommended': 220},
        {'code': '003', 'title': 'XTREME +EFB 60', 'rest_count': 0, 'price_opt': 100, 'price_recommended': 500},
    ]
    parser = _parser()
    with (
        caplog.at_level(logging.INFO),
        patch.object(PriceFiles, 'resolve', return_value=['plant.xls']),
        patch.object(PriceFiles, 'read_rows', return_value=rows),
    ):
        package = parser.parse()
    assert len(package.positions) == 2
    assert 'Обработано позиций - 2' in caplog.text
    assert 'Наценка (%) - Мин: 10.0, Макс: 25.0' in caplog.text
    assert 'Наценка (Руб.) - Мин: 20.0, Макс: 25.0' in caplog.text
    assert 'План-Т [batteries] // финиш' in caplog.text


def test_battery_parser_logs_empty_result(caplog: pytest.LogCaptureFixture) -> None:
    parser = _parser()
    with (
        caplog.at_level(logging.INFO),
        patch.object(PriceFiles, 'resolve', return_value=['plant.xls']),
        patch.object(PriceFiles, 'read_rows', return_value=[]),
    ):
        assert not parser.parse().positions
    assert 'Обработано позиций - 0' in caplog.text
    assert 'План-Т [batteries] // финиш' in caplog.text


@pytest.mark.parametrize('routed', [False, True])
def test_battery_parser_reads_real_json_price(tmp_path: Path, routed: bool, caplog: pytest.LogCaptureFixture) -> None:
    provider = FakeConfigProvider(tmp_path)
    price_folder = Path(provider.price_folder('plant'))
    price_folder.mkdir(parents=True)
    price_path = price_folder / 'battery.json'
    row = {'code': '001', 'title': '  XTREME   Arctic 60 ', 'rest_count': 1, 'price_recommended': '5500.25'}
    rows = [row]
    if routed:
        row['kind'] = 'battery'
        rows.append(
            {'code': 'other', 'title': 'Другая секция', 'rest_count': 1, 'price_recommended': '100', 'kind': 'other'}
        )
    price_path.write_text(json.dumps(rows))
    selected_section = {
        'id': 'plant_batteries',
        'file_templates': ['*.json'],
        'columns': ['code', 'title', 'rest_count', 'price_recommended'],
        'row_selector': {'column': 'kind', 'values': ['battery']},
    }
    sections = [selected_section]
    if routed:
        other_section = {'id': 'other', 'row_selector': {'column': 'kind', 'values': ['other']}}
        sections.append({**selected_section, **other_section})
    config = VendorConfig.from_dict(
        {
            'code': 'plant',
            'name': 'План-Т',
            'reader': 'json',
            'product_groups': [{'id': 'batteries', 'sections': sections}],
        },
        'plant',
        'plant.json',
    )
    group = config.product_groups[0]
    assert isinstance(group, BatteryConfig)
    section = group.sections[0]
    parser_params = ParserParams(
        supplier=ParseParamsSupplier('plant', section.name, section.id),
        start_row=section.start_row,
        sheet_info=section.sheet_info,
        columns=dict(section.columns),
        stop_words=(),
        file_templates=section.file_templates,
        sheet_indexes=section.sheet_indexes,
    )
    parse_config = make_parse_config(
        parser_params,
        config_provider=provider,
        vendor_section=section,
        vendor_config=config,
        routing=VendorRouting(config) if routed else None,
    )

    with caplog.at_level(logging.INFO):
        package = BatteryParser(parse_config, BatteryHandler(BatterySettings(), section.name)).parse()

    assert len(package.positions) == 1
    position = package.positions[0]
    assert position.identity.code == '001'
    assert position.identity.title == 'XTREME Arctic 60'
    assert position.identity.model == 'XTREME Arctic'
    assert str(position.offer.sale_price) == '5500.25'
    assert str(price_path) in caplog.text
