"""Загрузка прайсов поставщиков в file_prices."""

import json
import shutil
import zipfile
from collections.abc import Iterator, Mapping
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cfg import init_cfg
from domain.config_context import get_config_provider, set_config_provider
from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.file_config_provider import FileConfigProvider
from parsers.load_supplier_prices import load_supplier_prices, parse_prices_json
from parsers.supplier_file_rules import SupplierFileRules, vendor_file_rules
from parsers.supplier_price.errors import (
    InvalidPriceExtensionError,
    SupplierPriceFileNameError,
    SupplierPriceFileNotFoundError,
    SupplierPricesMappingError,
    UnknownSupplierCodeError,
)
from parsers.supplier_price.sources import PriceSources

_CATALOG = {
    '1': {'sup_code': 'poshk', 'sup_title': 'Пошк'},
    '3': {'sup_code': 'pioner', 'sup_title': 'Пионер'},
    '4': {'sup_code': 'mim', 'sup_title': 'Мим'},
    '7': {'sup_code': 'stk', 'sup_title': 'STK'},
    '2': {'sup_code': 'zapaska', 'sup_title': 'Запаска (диски)'},
}
_CATALOG_PATCH = 'parsers.load_supplier_prices.all_vendor_supplier_catalog'
_EXAMPLE_CONFIG = Path(__file__).resolve().parents[1] / 'parse_config_example'
_RULES_PATCH = 'parsers.load_supplier_prices.vendor_file_rules'
_DEFAULT_TEMPLATES = ('price*.xls', 'price*.xlsx')
_RULES = {
    'poshk': SupplierFileRules(_DEFAULT_TEMPLATES),
    'pioner': SupplierFileRules(_DEFAULT_TEMPLATES),
    'mim': SupplierFileRules(_DEFAULT_TEMPLATES, ('territories.json',)),
    'stk': SupplierFileRules(('price.xlsx',)),
    'zapaska': SupplierFileRules(('disk.json', 'tire.json')),
}
_XLS_BYTES = b'xls-content'
_XLSX_BYTES = b'xlsx-content'


@pytest.fixture(autouse=True)
def _file_rules() -> Iterator[None]:
    """Правила имён без чтения конфигов поставщиков (их проверяет test_vendor_file_rules_*)."""
    with patch(_RULES_PATCH, return_value=_RULES):
        yield


@pytest.fixture
def prices_root(fake_config_provider: FakeConfigProvider) -> Path:
    return Path(fake_config_provider.price_folder(''))


def _write_source(tmp_path: Path, name: str, file_bytes: bytes) -> Path:
    source = tmp_path / 'incoming' / name
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(file_bytes)
    return source


def _load(mapping: Mapping[str, PriceSources]) -> list[str]:
    """load_supplier_prices с активным провайдером путей."""
    return load_supplier_prices(mapping, get_config_provider())


def test_parse_prices_json_object() -> None:
    """валидный JSON-объект строк."""
    assert parse_prices_json('{"1": "/incoming/a.xls"}') == {'1': '/incoming/a.xls'}


def test_parse_prices_json_invalid() -> None:
    """не JSON."""
    with pytest.raises(SupplierPricesMappingError):
        parse_prices_json('not-json')


def test_parse_prices_json_not_object() -> None:
    """не объект."""
    with pytest.raises(SupplierPricesMappingError, match='Ожидается объект'):
        parse_prices_json('["1"]')


def test_parse_prices_json_empty_value() -> None:
    """пустой путь."""
    with pytest.raises(SupplierPricesMappingError, match='непустыми'):
        parse_prices_json('{"1": ""}')


def test_parse_prices_json_non_string_value() -> None:
    """путь не строка."""
    with pytest.raises(SupplierPricesMappingError, match='непустыми'):
        parse_prices_json('{"1": 1}')


def test_load_moves_and_renames(tmp_path: Path, prices_root: Path) -> None:
    """файл перемещается в папку поставщика как price.xls."""
    source = _write_source(tmp_path, 'any_price_name.xls', _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dests = _load({'1': str(source)})
    dest = prices_root / 'poshk' / 'price.xls'
    assert dests == [str(dest)]
    assert dest.read_bytes() == _XLS_BYTES
    assert not source.exists()


def test_load_xlsx_keeps_extension(tmp_path: Path, prices_root: Path) -> None:
    """xlsx сохраняет расширение."""
    source = _write_source(tmp_path, 'any.xlsx', _XLSX_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'1': str(source)})
    dest = prices_root / 'poshk' / 'price.xlsx'
    assert dest.read_bytes() == _XLSX_BYTES
    assert not source.exists()


def test_load_uppercase_extension(tmp_path: Path, prices_root: Path) -> None:
    """XLS → price.xls."""
    source = _write_source(tmp_path, 'any.XLS', _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'1': str(source)})
    assert (prices_root / 'poshk' / 'price.xls').is_file()


def test_load_creates_supplier_folder(tmp_path: Path, prices_root: Path) -> None:
    """папка поставщика создаётся."""
    source = _write_source(tmp_path, 'a.xls', _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'3': str(source)})
    assert (prices_root / 'pioner' / 'price.xls').is_file()


def test_load_replaces_other_extension(tmp_path: Path, prices_root: Path) -> None:
    """старый price.xls удаляется при загрузке xlsx."""
    dest_dir = prices_root / 'poshk'
    dest_dir.mkdir()
    old_xls = dest_dir / 'price.xls'
    old_xls.write_bytes(b'old')
    rest = dest_dir / 'rest.xls'
    rest.write_bytes(b'rest')
    source = _write_source(tmp_path, 'new.xlsx', _XLSX_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'1': str(source)})
    assert not old_xls.exists()
    assert (dest_dir / 'price.xlsx').read_bytes() == _XLSX_BYTES
    assert rest.read_bytes() == b'rest'


def test_load_already_in_place(prices_root: Path) -> None:
    """уже price.xls в папке поставщика — не трогаем."""
    dest_dir = prices_root / 'poshk'
    dest_dir.mkdir()
    dest = dest_dir / 'price.xls'
    dest.write_bytes(_XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dest_paths = _load({'1': str(dest)})
    assert dest_paths == [str(dest)]
    assert dest.read_bytes() == _XLS_BYTES


def test_load_two_suppliers(tmp_path: Path, prices_root: Path) -> None:
    """несколько поставщиков за один вызов."""
    first = _write_source(tmp_path, 'a.xls', _XLS_BYTES)
    second = _write_source(tmp_path, 'b.xlsx', _XLSX_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dests = _load({'1': str(first), '3': str(second)})
    assert dests == [
        str(prices_root / 'poshk' / 'price.xls'),
        str(prices_root / 'pioner' / 'price.xlsx'),
    ]


def test_load_rejects_extension(tmp_path: Path, prices_root: Path) -> None:
    """csv нельзя."""
    source = _write_source(tmp_path, 'a.csv', b'csv')
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(InvalidPriceExtensionError, match='csv'):
        _load({'1': str(source)})
    assert source.exists()


def test_load_rejects_json_not_in_templates(tmp_path: Path, prices_root: Path) -> None:
    """json, которого разбор поставщика не читает, — ошибка с перечнем масок."""
    source = _write_source(tmp_path, 'a.json', b'{}')
    with (
        patch(_CATALOG_PATCH, return_value=_CATALOG),
        pytest.raises(SupplierPriceFileNameError, match=r'a\.json.*price\*\.xls'),
    ):
        _load({'1': str(source)})
    assert source.exists()


def test_load_missing_file(tmp_path: Path, prices_root: Path) -> None:
    """нет файла."""
    missing = tmp_path / 'incoming' / 'gone.xls'
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(SupplierPriceFileNotFoundError):
        _load({'1': str(missing)})


def test_load_unknown_supplier(tmp_path: Path, prices_root: Path) -> None:
    """неизвестный ИД — до проверки файла."""
    source = _write_source(tmp_path, 'a.xls', _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(UnknownSupplierCodeError, match='99'):
        _load({'99': str(source)})
    assert source.exists()


def test_load_by_sup_code(tmp_path: Path, prices_root: Path) -> None:
    """ключ — sup_code, не ИД."""
    source = _write_source(tmp_path, 'any.xls', _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dests = _load({'poshk': str(source)})
    dest = prices_root / 'poshk' / 'price.xls'
    assert dests == [str(dest)]
    assert dest.read_bytes() == _XLS_BYTES
    assert not source.exists()


def test_load_mixed_id_and_sup_code(tmp_path: Path, prices_root: Path) -> None:
    """ИД и sup_code в одной карте."""
    first = _write_source(tmp_path, 'a.xls', _XLS_BYTES)
    second = _write_source(tmp_path, 'b.xlsx', _XLSX_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dests = _load({'1': str(first), 'pioner': str(second)})
    assert dests == [
        str(prices_root / 'poshk' / 'price.xls'),
        str(prices_root / 'pioner' / 'price.xlsx'),
    ]


def test_load_unknown_sup_code(tmp_path: Path, prices_root: Path) -> None:
    """неизвестный sup_code — до проверки файла."""
    source = _write_source(tmp_path, 'a.xls', _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(UnknownSupplierCodeError, match='nope'):
        _load({'nope': str(source)})
    assert source.exists()


def test_load_validates_all_before_move(tmp_path: Path, prices_root: Path) -> None:
    """ошибка второго файла — первый не перемещается."""
    good = _write_source(tmp_path, 'a.xls', _XLS_BYTES)
    bad = _write_source(tmp_path, 'b.csv', b'csv')
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(InvalidPriceExtensionError):
        _load({'1': str(good), '3': str(bad)})
    assert good.exists()
    assert not (prices_root / 'poshk' / 'price.xls').exists()


def test_load_empty_mapping(prices_root: Path) -> None:
    """пустая карта — пустой список."""
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        assert _load({}) == []


def test_load_supplier_prices_creates_nested_supplier_folder(tmp_path: Path) -> None:
    """Папка file_prices/<sup_code> создаётся целиком: parents=True, а не exist_ok."""
    root = tmp_path / 'env'
    assert not root.exists()
    init_cfg(FileConfigProvider(str(root)))
    source = _write_source(tmp_path, 'poshk.xlsx', _XLSX_BYTES)

    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        found = _load({'1': str(source)})

    price_file = root / 'file_prices' / 'poshk' / 'price.xlsx'
    assert found == [str(price_file)]
    assert price_file.read_bytes() == _XLSX_BYTES


def test_parse_prices_json_invalid_message_has_cause() -> None:
    """Сообщение о битом JSON содержит причину разбора, а не None."""
    with pytest.raises(SupplierPricesMappingError, match='Expecting value'):
        parse_prices_json('not-json')


def test_load_missing_file_message_has_path(tmp_path: Path, prices_root: Path) -> None:
    """Сообщение об отсутствующем прайсе называет сам файл, а не None."""
    missing = tmp_path / 'incoming' / 'gone.xls'

    with (
        patch(_CATALOG_PATCH, return_value=_CATALOG),
        pytest.raises(SupplierPriceFileNotFoundError, match=r'gone\.xls'),
    ):
        _load({'1': str(missing)})


def _write_zip(tmp_path: Path, name: str, members: dict[str, bytes]) -> Path:
    archive = tmp_path / 'incoming' / name
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, 'w') as zip_file:
        for member, member_bytes in members.items():
            zip_file.writestr(member, member_bytes)
    return archive


def test_parse_prices_json_list() -> None:
    """список путей — кортеж."""
    assert parse_prices_json('{"4": ["/a.xlsx", "/territories.json"]}') == {'4': ('/a.xlsx', '/territories.json')}


@pytest.mark.parametrize('raw', ['{"4": []}', '{"4": ["/a.xlsx", ""]}', '{"4": ["/a.xlsx", 1]}', '{"": "/a.xls"}'])
def test_parse_prices_json_bad_list(raw: str) -> None:
    """пустой список, пустой или не строковый путь, пустой ключ."""
    with pytest.raises(SupplierPricesMappingError, match='непустыми'):
        parse_prices_json(raw)


def test_load_price_with_territories(tmp_path: Path, prices_root: Path) -> None:
    """прайс МИМ переименовывается, territories.json сохраняет имя."""
    price = _write_source(tmp_path, 'Прайс МИМ.xlsx', _XLSX_BYTES)
    territories = _write_source(tmp_path, 'territories.json', b'[]')
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dests = _load({'4': (str(price), str(territories))})
    dest_dir = prices_root / 'mim'
    assert dests == [str(dest_dir / 'territories.json'), str(dest_dir / 'price.xlsx')]
    assert (dest_dir / 'price.xlsx').read_bytes() == _XLSX_BYTES
    assert (dest_dir / 'territories.json').read_bytes() == b'[]'


def test_load_price_keeps_old_territories(tmp_path: Path, prices_root: Path) -> None:
    """новый прайс без territories.json — прежний список складов остаётся, старый прайс удаляется."""
    dest_dir = prices_root / 'mim'
    dest_dir.mkdir()
    (dest_dir / 'territories.json').write_bytes(b'[1]')
    (dest_dir / 'price_old.xls').write_bytes(b'old')
    source = _write_source(tmp_path, 'new.xlsx', _XLSX_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'4': str(source)})
    assert sorted(path.name for path in dest_dir.iterdir()) == ['price.xlsx', 'territories.json']
    assert (dest_dir / 'territories.json').read_bytes() == b'[1]'


def test_load_only_json_keeps_excel_prices(tmp_path: Path, prices_root: Path) -> None:
    """пришёл только territories.json — Excel-прайсы поставщика не трогаются, json заменяется."""
    dest_dir = prices_root / 'mim'
    dest_dir.mkdir()
    (dest_dir / 'price.xlsx').write_bytes(b'old-price')
    (dest_dir / 'territories.json').write_bytes(b'[1]')
    source = _write_source(tmp_path, 'territories.json', b'[2]')
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'4': str(source)})
    assert (dest_dir / 'price.xlsx').read_bytes() == b'old-price'
    assert (dest_dir / 'territories.json').read_bytes() == b'[2]'


def test_load_several_excel_get_numbered_names(tmp_path: Path, prices_root: Path) -> None:
    """Excel без подходящих имён — price, price_2 (номер у каждого расширения свой); подходящее имя не меняется."""
    first = _write_source(tmp_path, 'a.xlsx', b'a')
    second = _write_source(tmp_path, 'b.xlsx', b'b')
    third = _write_source(tmp_path, 'c.xls', b'c')
    kept = _write_source(tmp_path, 'price_trucks.xlsx', b'd')
    sources = [str(path) for path in (first, second, third, kept)]
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'1': sources})
    dest_dir = prices_root / 'poshk'
    assert sorted(path.name for path in dest_dir.iterdir()) == [
        'price.xls',
        'price.xlsx',
        'price_2.xlsx',
        'price_trucks.xlsx',
    ]
    assert (dest_dir / 'price.xlsx').read_bytes() == b'a'
    assert (dest_dir / 'price_2.xlsx').read_bytes() == b'b'
    assert (dest_dir / 'price.xls').read_bytes() == b'c'
    assert (dest_dir / 'price_trucks.xlsx').read_bytes() == b'd'


def test_load_generated_name_skips_taken(tmp_path: Path, prices_root: Path) -> None:
    """имя price.xlsx уже занято присланным файлом — переименованный получает price_2.xlsx."""
    exact = _write_source(tmp_path, 'price.xlsx', b'exact')
    other = _write_source(tmp_path, 'other.xlsx', b'other')
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'1': [str(other), str(exact)]})
    dest_dir = prices_root / 'poshk'
    assert (dest_dir / 'price.xlsx').read_bytes() == b'exact'
    assert (dest_dir / 'price_2.xlsx').read_bytes() == b'other'


def test_load_single_template_rejects_second_excel(tmp_path: Path, prices_root: Path) -> None:
    """у STK маска только price.xlsx — второй Excel положить некуда, ничего не перемещается."""
    first = _write_source(tmp_path, 'a.xlsx', b'a')
    second = _write_source(tmp_path, 'b.xlsx', b'b')
    with (
        patch(_CATALOG_PATCH, return_value=_CATALOG),
        pytest.raises(SupplierPriceFileNameError, match=r'b\.xlsx.*STK|b\.xlsx.*stk'),
    ):
        _load({'7': [str(first), str(second)]})
    assert first.exists()
    assert not (prices_root / 'stk').exists()


def test_load_xls_for_xlsx_only_supplier(tmp_path: Path, prices_root: Path) -> None:
    """xls поставщику с маской price.xlsx — ошибка: разбор его не прочитает."""
    source = _write_source(tmp_path, 'a.xls', _XLS_BYTES)
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(SupplierPriceFileNameError):
        _load({'7': str(source)})


def test_load_json_templates_keep_names(tmp_path: Path, prices_root: Path) -> None:
    """json по маскам поставщика (Запаска) кладутся как есть."""
    disk = _write_source(tmp_path, 'disk.json', b'{"d": 1}')
    tire = _write_source(tmp_path, 'tire.json', b'{"t": 1}')
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'2': [str(disk), str(tire)]})
    assert (prices_root / 'zapaska' / 'disk.json').read_bytes() == b'{"d": 1}'
    assert (prices_root / 'zapaska' / 'tire.json').read_bytes() == b'{"t": 1}'


def test_load_zip_flattens_and_skips_service_files(tmp_path: Path, prices_root: Path) -> None:
    """zip: папки внутри архива не важны, __MACOSX и скрытые файлы пропускаются, архив остаётся."""
    archive = _write_zip(
        tmp_path,
        'mim.zip',
        {
            'выгрузка/Прайс.xlsx': _XLSX_BYTES,
            'выгрузка/territories.json': b'[]',
            'выгрузка/': b'',
            '__MACOSX/выгрузка/._Прайс.xlsx': b'junk',
            'выгрузка/.DS_Store': b'junk',
        },
    )
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        _load({'4': str(archive)})
    dest_dir = prices_root / 'mim'
    assert sorted(path.name for path in dest_dir.iterdir()) == ['price.xlsx', 'territories.json']
    assert (dest_dir / 'price.xlsx').read_bytes() == _XLSX_BYTES


def test_load_zip_member_path_stays_inside(tmp_path: Path, prices_root: Path) -> None:
    """запись архива с `../` кладётся по имени файла, а не по пути из архива."""
    archive = _write_zip(tmp_path, 'evil.zip', {'../../price.xlsx': _XLSX_BYTES})
    with patch(_CATALOG_PATCH, return_value=_CATALOG):
        dests = _load({'1': str(archive)})
    assert dests == [str(prices_root / 'poshk' / 'price.xlsx')]
    assert not (tmp_path / 'price.xlsx').exists()


def test_load_zip_duplicate_names(tmp_path: Path, prices_root: Path) -> None:
    """два territories.json из разных папок архива — ошибка, а не тихая перезапись."""
    archive = _write_zip(tmp_path, 'mim.zip', {'a/territories.json': b'[1]', 'b/territories.json': b'[2]'})
    with (
        patch(_CATALOG_PATCH, return_value=_CATALOG),
        pytest.raises(SupplierPriceFileNameError, match=r'territories\.json'),
    ):
        _load({'4': str(archive)})
    assert not (prices_root / 'mim').exists()


def test_load_zip_rejects_inner_extension(tmp_path: Path, prices_root: Path) -> None:
    """csv в архиве — ошибка расширения с именем файла."""
    archive = _write_zip(tmp_path, 'p.zip', {'list.csv': b'csv'})
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(InvalidPriceExtensionError, match=r'list\.csv'):
        _load({'1': str(archive)})


def test_load_empty_zip(tmp_path: Path, prices_root: Path) -> None:
    """архив без файлов."""
    archive = _write_zip(tmp_path, 'empty.zip', {'folder/': b''})
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(SupplierPriceFileNotFoundError, match='empty'):
        _load({'1': str(archive)})


def test_load_broken_zip(tmp_path: Path, prices_root: Path) -> None:
    """файл .zip, который не архив."""
    archive = _write_source(tmp_path, 'broken.zip', b'not a zip')
    with patch(_CATALOG_PATCH, return_value=_CATALOG), pytest.raises(InvalidPriceExtensionError, match='broken'):
        _load({'1': str(archive)})


def test_load_zip_temp_folder_removed(tmp_path: Path, prices_root: Path) -> None:
    """временная папка распаковки удаляется и после ошибки."""
    archive = _write_zip(tmp_path, 'p.zip', {'x.csv': b'csv'})
    unpack_root = tmp_path / 'tmp'
    unpack_root.mkdir()
    with (
        patch(_CATALOG_PATCH, return_value=_CATALOG),
        patch('tempfile.tempdir', str(unpack_root)),
        pytest.raises(InvalidPriceExtensionError),
    ):
        _load({'1': str(archive)})
    assert list(unpack_root.iterdir()) == []


def test_supplier_file_rules_accepts() -> None:
    """маска, служебное имя и регистр."""
    rules = SupplierFileRules(_DEFAULT_TEMPLATES, ('territories.json',))
    assert rules.accepts('price_2.xlsx')
    assert rules.accepts('territories.json')
    assert not rules.accepts('Price.xlsx')
    assert not rules.accepts('other.json')
    assert rules.is_excel_price('price.xls')
    assert not rules.is_excel_price('territories.json')
    assert rules.expected() == 'price*.xls, price*.xlsx, territories.json'


def test_vendor_file_rules_from_configs(tmp_path: Path) -> None:
    """маски собираются со всех секций; territories.json — только при warehouse_cities."""
    config_folder = tmp_path / 'parse_config'
    shutil.copytree(_EXAMPLE_CONFIG, config_folder)
    mim_path = config_folder / 'vendors' / 'mim.json'
    mim = json.loads(mim_path.read_text(encoding='utf-8'))
    mim.setdefault('behavior', {})['warehouse_cities'] = ['Новосибирск']
    mim_path.write_text(json.dumps(mim, ensure_ascii=False), encoding='utf-8')
    set_config_provider(FakeConfigProvider(tmp_path, config_folder=config_folder))

    rules = vendor_file_rules()

    assert rules['zapaska'] == SupplierFileRules(('disk.json', 'tire.json'))
    assert rules['poshk'] == SupplierFileRules(_DEFAULT_TEMPLATES)
    assert rules['mim'] == SupplierFileRules(_DEFAULT_TEMPLATES, ('territories.json',))


def test_place_files_folder_comes_from_injected_provider(tmp_path: Path) -> None:
    """файлы кладутся в папку переданного провайдера, а не глобального"""
    source = tmp_path / 'price.xlsx'
    source.write_bytes(b'x')
    dest = tmp_path / 'custom_prices'
    injected = MagicMock()
    injected.price_folder.return_value = str(dest)

    found = load_supplier_prices({'1': str(source)}, injected)

    assert found == [str(dest / 'price.xlsx')]
