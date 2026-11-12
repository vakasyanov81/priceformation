"""Итоговый лог аккумуляторной секции через настоящий парсер и обработчик."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from parsers.base_parser.base_parser_config import ParseParamsSupplier, ParserParams, make_parse_config
from parsers.base_parser.price_files import PriceFiles
from parsers.battery.handler import BatteryHandler
from parsers.battery.parser import BatteryParser
from parsers.vendor_config.battery_settings import BatterySettings


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
