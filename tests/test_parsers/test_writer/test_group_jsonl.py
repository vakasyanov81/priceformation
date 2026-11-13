"""JSONL v2: независимость моделей, схем, кодов и повторных запусков."""

import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest

from domain.exceptions import ConfigValidationError
from domain.product_groups import ProductGroup
from parsers.writer.group_files import GroupFileWriter
from parsers.writer.jsonl_meta import RESULT_META_FILE, read_registry
from parsers.writer.templates.group_output import OutputMode
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xlsxwriter_adapter import XlsxWriterAdapter
from tests.group_output_examples import OtherOutputSource
from tests.test_domain.group_handler_examples import TestGroupResult, TestPosition
from tests.test_parsers.test_writer.test_group_files import DATE, OTHER, TIRES, _output, _sources


def _write(folder: Path, *, workbook: bool = False, empty: bool = False) -> list[str]:
    output = _output()
    if workbook:
        groups = tuple(replace(group, file_name=None) for group in output.groups)
        output = replace(output, groups=groups, mode=OutputMode.WORKBOOK_SHEETS, file_name='all_{now}.xlsx')
    sources = _sources()
    labels: tuple[TestPosition, ...] = (TestPosition('Другая модель'),) * 2 + (TestPosition('@1'),)
    if empty:
        labels = ()
    sources[OTHER] = OtherOutputSource(TestGroupResult(labels))
    writer = GroupFileWriter(xls_writer=XlsWriter, write_driver=XlsxWriterAdapter, result_folder=str(folder))
    return writer.write([output], sources, current_date=DATE, as_jsonl=True)


@pytest.mark.parametrize('workbook', [False, True])
def test_group_streams_have_local_schemas_and_codes(tmp_path: Path, workbook: bool) -> None:
    """Колонка 1 и код @N имеют собственный смысл в каждом файле."""
    paths = _write(tmp_path, workbook=workbook)
    expected = [f'all_{DATE}_{group}.jsonl' for group in (TIRES, OTHER)]
    if not workbook:
        expected = [f'tires_{DATE}.jsonl', f'other_{DATE}.jsonl']
    assert [Path(path).name for path in paths] == expected
    registry = read_registry(tmp_path)
    tire_schema, other_schema = [registry[name] for name in expected]
    assert tire_schema['columns'] == {'1': 'Шинное название'}
    assert other_schema['columns'] == {'1': 'Метка'}
    assert not tire_schema['value_codes']
    assert other_schema['value_codes'] == {'@2': 'Другая модель'}
    assert Path(paths[0]).read_text(encoding='utf-8') == '{"1":"Шина"}\n'
    lines = Path(paths[1]).read_text(encoding='utf-8').splitlines()
    assert lines == ['{"1":"@2"}', '{"1":"@2"}', '{"1":"@1"}']
    assert other_schema['template_id'] == 'example'
    assert other_schema['product_group'] == ProductGroup.BATTERIES
    assert other_schema['schema_version'] == 1


def test_empty_group_replaces_rows_and_codes(tmp_path: Path) -> None:
    """Новый пустой пакет заменяет файл и локальные коды; соседний поток сохраняется."""
    paths = _write(tmp_path)
    tire_bytes = Path(paths[0]).read_bytes()
    _write(tmp_path, empty=True)
    assert Path(paths[1]).read_bytes() == b''
    schema = read_registry(tmp_path)[Path(paths[1]).name]
    assert schema['columns'] == {'1': 'Метка'}
    assert not schema['value_codes']
    assert Path(paths[0]).read_bytes() == tire_bytes


@pytest.mark.parametrize(
    'payload',
    [
        '{',
        '[]',
        '{"1":"Название"}',
        '{"version":1,"files":{}}',
        '{"version":3,"files":{}}',
        '{"version":2,"files":{},"values":{}}',
        '{"version":true,"files":{}}',
        '{"version":2,"files":[]}',
        '{"version":2,"files":{"../bad.jsonl":{}}}',
        '{"version":2,"files":{"bad.jsonl":[]}}',
    ],
)
def test_invalid_registry_prevents_all_writes(tmp_path: Path, payload: str) -> None:
    """Неверные и старые метаданные отклоняются с путём до изменения потоков."""
    path = tmp_path / RESULT_META_FILE
    path.write_text(payload, encoding='utf-8')
    existing = tmp_path / f'tires_{DATE}.jsonl'
    existing.write_bytes(b'old')
    with pytest.raises(ConfigValidationError, match=r'result_meta.json.*пересоздайте'):
        _write(tmp_path)
    assert path.read_text(encoding='utf-8') == payload
    assert existing.read_bytes() == b'old'
    assert len(list(tmp_path.iterdir())) == 2


@pytest.mark.parametrize(
    'identity,replacement', [('template_id', 'foreign'), ('product_group', OTHER), ('schema_version', 2)]
)
def test_foreign_file_identity_prevents_replacement(tmp_path: Path, identity: str, replacement: object) -> None:
    """Существующий файл нельзя незаметно присвоить другой паре шаблон–группа."""
    paths = _write(tmp_path)
    meta = tmp_path / RESULT_META_FILE
    payload = json.loads(meta.read_text(encoding='utf-8'))
    payload['files'][Path(paths[0]).name][identity] = replacement
    meta.write_text(json.dumps(payload), encoding='utf-8')
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    with pytest.raises(ConfigValidationError, match='пересоздайте'):
        _write(tmp_path)
    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == before


def test_unregistered_existing_stream_is_rejected(tmp_path: Path) -> None:
    existing = tmp_path / f'other_{DATE}.jsonl'
    existing.write_bytes(b'old')
    with pytest.raises(ConfigValidationError, match='other_'):
        _write(tmp_path)
    assert list(tmp_path.iterdir()) == [existing]
    assert existing.read_bytes() == b'old'


def test_no_selected_groups_create_no_metadata(tmp_path: Path) -> None:
    folder = tmp_path / 'absent'
    writer = GroupFileWriter(xls_writer=XlsWriter, write_driver=XlsxWriterAdapter, result_folder=str(folder))
    sources = _sources()
    paths = writer.write([_output()], sources, selected=set(), as_jsonl=True)
    assert not paths
    assert not folder.exists()


def test_failed_publication_restores_existing_results(tmp_path: Path) -> None:
    """Ошибка замены реестра не оставляет новые потоки со старой схемой."""
    _write(tmp_path)
    before = {path.name: path.read_bytes() for path in tmp_path.iterdir()}
    original_replace = Path.replace

    def replace_file(source: Path, target: Path) -> Path:
        if target.name == RESULT_META_FILE:
            raise OSError('test publication failure')
        return original_replace(source, target)

    with patch.object(Path, 'replace', replace_file), pytest.raises(OSError, match='publication'):
        _write(tmp_path, empty=True)
    assert {path.name: path.read_bytes() for path in tmp_path.iterdir()} == before


def test_other_registry_entries_survive_new_output(tmp_path: Path) -> None:
    """Новый шаблон не расширяет коды или схемы ранее записанных файлов."""
    paths = _write(tmp_path)
    before = read_registry(tmp_path)
    _write(tmp_path, workbook=True)
    registry = read_registry(tmp_path)
    assert len(registry) == 4
    for path in paths:
        name = Path(path).name
        assert registry[name] == before[name]


@pytest.mark.parametrize(
    'schema_patch',
    [
        {'template_id': ''},
        {'product_group': 'unknown'},
        {'schema_version': True},
        {'schema_version': 0},
        {'columns': []},
        {'columns': {'0': 'wrong'}},
        {'columns': {'1': 9}},
        {'value_codes': {'invalid': 'text'}},
        {'unexpected': True},
    ],
)
def test_malformed_file_schema_is_rejected(tmp_path: Path, schema_patch: dict[str, object]) -> None:
    _write(tmp_path)
    path = tmp_path / RESULT_META_FILE
    payload = json.loads(path.read_text(encoding='utf-8'))
    schema = next(iter(payload['files'].values()))
    schema.update(schema_patch)
    path.write_text(json.dumps(payload), encoding='utf-8')
    with pytest.raises(ConfigValidationError, match='пересоздайте'):
        _write(tmp_path)


@pytest.mark.parametrize('foreign_name', ['TIRES_2026-11-12.jsonl', './extra.jsonl', '/absolute.jsonl'])
def test_registry_paths_are_unique_and_relative(tmp_path: Path, foreign_name: str) -> None:
    _write(tmp_path)
    path = tmp_path / RESULT_META_FILE
    payload = json.loads(path.read_text(encoding='utf-8'))
    files = payload['files']
    files[foreign_name] = next(iter(files.values()))
    path.write_text(json.dumps(payload), encoding='utf-8')
    with pytest.raises(ConfigValidationError, match='пересоздайте'):
        _write(tmp_path)


def test_same_code_has_different_meanings_between_groups(tmp_path: Path) -> None:
    """Две разные модели используют @1 для разных значений одного запуска."""
    from domain.product_group_result import TireAndDiskResult
    from domain.row_item.row_item import RowItem
    from parsers.common_price.tire_output import TireOutputSource

    output = _output()
    columns = [{'Название': {'field': 'title'}}, {'Сезон': {'field': 'season'}}]
    tire_settings = replace(output.groups[0], columns=columns)
    output = replace(output, groups=(tire_settings, output.groups[1]))
    sources = _sources()
    raw_row = {'title': 'Зимняя', 'season': 'Зимняя'}
    rows = tuple(RowItem(raw_row) for _ in range(2))
    sources[TIRES] = TireOutputSource(TireAndDiskResult(rows))
    sources[OTHER] = OtherOutputSource(TestGroupResult((TestPosition('Другая модель'),) * 2))
    writer = GroupFileWriter(xls_writer=XlsWriter, write_driver=XlsxWriterAdapter, result_folder=str(tmp_path))
    paths = writer.write([output], sources, current_date=DATE, as_jsonl=True)
    registry = read_registry(tmp_path)
    tire_file, other_file = map(Path, paths)
    assert registry[tire_file.name]['value_codes'] == {'@1': 'Зимняя'}
    assert registry[other_file.name]['value_codes'] == {'@1': 'Другая модель'}
    lines = tire_file.read_text(encoding='utf-8').splitlines()
    first = json.loads(lines[0])
    assert first == {'1': 'Зимняя', '2': '@1'}


@pytest.mark.parametrize('version', [0, -1, True])
def test_invalid_output_schema_version_prevents_files(tmp_path: Path, version: int) -> None:
    output = _output()
    group = replace(output.groups[0], schema_version=version)
    output = replace(output, groups=(group, output.groups[1]))
    writer = GroupFileWriter(xls_writer=XlsWriter, write_driver=XlsxWriterAdapter, result_folder=str(tmp_path))
    with pytest.raises(ConfigValidationError, match='schema_version'):
        writer.write([output], _sources(), as_jsonl=True)
    assert not list(tmp_path.iterdir())


def test_invalid_utf8_metadata_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / RESULT_META_FILE
    path.write_bytes(b'\xff')
    with pytest.raises(ConfigValidationError, match=r'result_meta\.json'):
        _write(tmp_path)
    assert list(tmp_path.iterdir()) == [path]
    assert path.read_bytes() == b'\xff'


def test_failed_first_publication_removes_new_streams(tmp_path: Path) -> None:
    original_replace = Path.replace

    def replace_file(source: Path, target: Path) -> Path:
        if target.name == RESULT_META_FILE:
            raise OSError('test publication failure')
        return original_replace(source, target)

    with patch.object(Path, 'replace', replace_file), pytest.raises(OSError, match='publication'):
        _write(tmp_path)
    assert not list(tmp_path.iterdir())


def test_registry_case_change_cannot_claim_existing_file(tmp_path: Path) -> None:
    _write(tmp_path)
    path = tmp_path / RESULT_META_FILE
    payload = json.loads(path.read_text(encoding='utf-8'))
    files = payload['files']
    name = f'tires_{DATE}.jsonl'
    foreign_name = f'TIRES_{DATE}.jsonl'
    files[foreign_name] = files.pop(name)
    (tmp_path / name).rename(tmp_path / foreign_name)
    path.write_text(json.dumps(payload), encoding='utf-8')
    with pytest.raises(ConfigValidationError, match='пересоздайте'):
        _write(tmp_path)
