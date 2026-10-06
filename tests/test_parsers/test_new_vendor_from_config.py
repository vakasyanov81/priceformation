"""Новый поставщик = 1 JSON без правки Python.

Поднимается фиктивный конфиг поставщика из JSON, строится config-driven парсер
и разбирается фейковый прайс — без единой строчки Python кроме теста.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cfg import init_cfg
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.config_driven_parser import make_config_driven_parser
from parsers.base_parser.file_reader import FileReader
from parsers.registry import clear_registry, make_vendor_entry

# Тестовые данные прайса
_TEST_ROWS = [
    {'title': '205/55R16', 'price_opt': 5000, 'rest_count': 10},
    {'title': '195/65R15', 'price_opt': 3500, 'rest_count': 5},
]


class _FakeDataReader:
    """Reader, возвращающий тестовые строки с переименованием колонок."""

    @classmethod
    def get_instance(cls, file_path: str, reader_params: dict[str, Any]) -> _FakeDataReader:
        return cls(file_path, reader_params)

    def __init__(self, file_path: str, reader_params: dict[str, Any]) -> None:
        self.file_path = file_path
        self.reader_params = reader_params
        self.columns = reader_params.get('columns', {})

    def parse(self, sheet_indexes: Any = None) -> list[dict[str, Any]]:
        """Вернуть тестовые строки, переименовав колонки в ключи RowItem."""
        mapped: list[dict[str, Any]] = []
        keys = list(_TEST_ROWS[0].keys()) if _TEST_ROWS else []
        for row in _TEST_ROWS:
            mapped_row: dict[str, Any] = {
                field_name: row[keys[flat_key]]
                for flat_key, field_name in self.columns.items()
                if isinstance(flat_key, int) and flat_key < len(keys)
            }
            mapped.append(mapped_row)
        return mapped


def test_new_vendor_from_json_config(tmp_path: Path) -> None:
    """Новый поставщик: JSON-конфиг → парсер → разбор → строки."""
    config_root = tmp_path / 'parse_config'
    vendors_dir = config_root / 'vendors'
    vendors_dir.mkdir(parents=True)
    (config_root / 'black_list').write_text('', encoding='utf-8')
    (config_root / 'manufacturer_aliases.json').write_text('{}', encoding='utf-8')

    import json

    (vendors_dir / 'test_vendor.json').write_text(
        json.dumps(
            {
                'enabled': 1,
                'code': 't1',
                'name': 'Тестовый поставщик',
                'start_row': 2,
                'file_templates': ['price*.xls*'],
                'sections': [
                    {
                        'name': 'Основной',
                        'sheet_indexes': [0],
                        'columns': {
                            '0': 'title',
                            '1': 'price_opt',
                            '2': 'rest_count',
                        },
                        'pricing': {
                            'policy': 'map_on_opt',
                            'rules': {
                                'markup_rules': {
                                    'r1': {'min': 0, 'max': 10000, 'percent': 0.20},
                                },
                            },
                        },
                    },
                ],
            },
            ensure_ascii=False,
        )
    )

    init_cfg(
        FakeConfigProvider(
            tmp_path,
            config_folder=config_root,
            prices_folder=tmp_path / 'file_prices',
            result_folder=tmp_path / 'file_prices' / 'result',
        )
    )
    clear_registry()

    from parsers.vendor_config.provider import load_vendor_configs

    cfgs = load_vendor_configs()
    vendor_cfg = cfgs['test_vendor']

    section = vendor_cfg.sections[0]
    entry = make_vendor_entry(section, vendor_cfg)
    parse_config = entry[1]

    parser = make_config_driven_parser(section, vendor_cfg, parse_config)
    parser.data_reader = _FakeDataReader
    parser._file_reader_impl = FileReader(data_reader=_FakeDataReader)
    parser.files = ['price_test.xls']

    parsed = parser.parse()

    assert len(parsed) == 2, f'Ожидалось 2 строки, получено {len(parsed)}'

    row0 = parsed[0]
    assert row0.identity.title == '205/55R16'
    assert row0.pricing.price_opt == 5000
    assert row0.stock.rest_count == 10
    assert row0.pricing.price_markup == 6000  # 5000 + 20%

    row1 = parsed[1]
    assert row1.identity.title == '195/65R15'
    assert row1.pricing.price_opt == 3500
    assert row1.stock.rest_count == 5
    assert row1.pricing.price_markup == 4200  # 3500 + 20%


def test_new_vendor_has_no_python_code(tmp_path: Path) -> None:
    """Верификация: для нового поставщика не нужно импортировать Python-модуль вендора."""
    config_root = tmp_path / 'parse_config'
    vendors_dir = config_root / 'vendors'
    vendors_dir.mkdir(parents=True)

    import json

    (vendors_dir / 'minimal.json').write_text(
        json.dumps(
            {
                'enabled': 1,
                'code': 'm1',
                'name': 'Минимальный',
                'start_row': 1,
                'file_templates': ['data.json'],
                'sections': [
                    {
                        'name': 'Раздел 1',
                        'sheet_indexes': [0],
                        'columns': {'0': 'code', '1': 'title'},
                    },
                ],
            }
        )
    )

    init_cfg(
        FakeConfigProvider(
            tmp_path,
            config_folder=config_root,
            prices_folder=tmp_path / 'file_prices',
            result_folder=tmp_path / 'file_prices' / 'result',
        )
    )
    clear_registry()

    from parsers.registry import vendor_entry_for

    parser_cls, parse_config = vendor_entry_for('m1')

    assert parser_cls is BaseParser
    assert parse_config.supplier.code == 'm1'  # id секции
    assert parse_config.supplier.name == 'Раздел 1'  # section.name
    assert parse_config._vendor_config.name == 'Минимальный'  # vendor.name
