"""Схема прайса: шапки используемых колонок и сравнение «было → стало»."""

import json
from pathlib import Path

import openpyxl
import pytest

from parsers.price_schema.diff import compare_schemas
from parsers.price_schema.models import FileHead, PriceSchema, SheetHead
from parsers.price_schema.schema import build_schema, read_file_head

_COLUMNS: dict[int | str, str] = {0: 'code', 2: 'title'}
_EXCEL_COLUMN_CASES = (
    (0, 'A'),
    (25, 'Z'),
    (26, 'AA'),
    (701, 'ZZ'),
    (702, 'AAA'),
    (16383, 'XFD'),
)


def _head(*rows: tuple[object, ...], name: str = 'Лист') -> FileHead:
    return FileHead(sheets=(SheetHead(name, rows),))


def _schema(head: FileHead, start_row: int) -> PriceSchema:
    return build_schema(head, start_row=start_row, sheet_indexes=(0,), columns=_COLUMNS)


def _changes(old: FileHead, new: FileHead, *, start_row: int = 3) -> list[str]:
    return compare_schemas(_schema(old, start_row), _schema(new, start_row), _COLUMNS)


def test_only_selected_sheets_are_compared() -> None:
    old = FileHead(
        sheets=(
            SheetHead('Первый', (('Старый', 'Цена', 'Название'),)),
            SheetHead('Второй', (('Артикул', 'Цена', 'Название'),)),
        )
    )
    new = FileHead(
        sheets=(
            SheetHead('Первый', (('Новый', 'Цена', 'Название'),)),
            SheetHead('Второй', (('Артикул', 'Цена', 'Название'),)),
        )
    )
    selected = (1,)

    before = build_schema(old, start_row=2, sheet_indexes=selected, columns=_COLUMNS)
    after = build_schema(new, start_row=2, sheet_indexes=selected, columns=_COLUMNS)

    assert set(before.sheets) == {1}
    assert compare_schemas(before, after, _COLUMNS) == []


def test_sheet_index_equal_to_sheet_count_is_ignored() -> None:
    head = FileHead(sheets=(SheetHead('Первый', ()), SheetHead('Второй', ())))

    schema = build_schema(head, start_row=2, sheet_indexes=(2,), columns=_COLUMNS)

    assert schema.sheets == {}


def test_first_data_row_has_no_header_rows() -> None:
    schema = _schema(_head(('Артикул', 'Цена', 'Название')), start_row=1)

    assert schema.sheets[0].headers == {}


def test_short_header_row_has_no_column_cell() -> None:
    schema = _schema(_head(('Артикул',)), start_row=2)

    assert schema.sheets[0].headers == {0: 'Артикул'}


def test_same_schema_no_changes() -> None:
    """одинаковые шапки — расхождений нет, даже если заголовок над шапкой (дата) другой."""
    old = _head(('Прайс на 1 января', None, None), ('Артикул', 'Цена', 'Название'))
    new = _head(('Прайс на 8 января', None, None), ('Артикул', 'Цена', 'Название'))

    assert _changes(old, new) == []


def test_header_changed_names_column_and_usage() -> None:
    """смена заголовка называет колонку (буква Excel) и поле, в которое она разбирается."""
    old = _head(('Артикул', 'Цена', 'Название'))
    new = _head(('Артикул', 'Цена', 'Наименование'))

    assert _changes(old, new, start_row=2) == [
        'вкладка «Лист», колонка C: заголовок «Название» → «Наименование» (используется как «title»)',
    ]


def test_unused_column_change_is_ignored() -> None:
    """колонка, которую парсер не читает, предупреждений не даёт."""
    old = _head(('Артикул', 'Цена', 'Название'))
    new = _head(('Артикул', 'Скидка', 'Название'))

    assert _changes(old, new, start_row=2) == []


def test_header_disappeared_and_appeared() -> None:
    """пропавший и появившийся заголовок описываются отдельно."""
    old = _head(('Артикул', None, 'Название'))
    new = _head((None, None, 'Название'))
    assert _changes(old, new, start_row=2) == [
        'вкладка «Лист», колонка A: пропал заголовок «Артикул» (используется как «code»)',
    ]
    assert _changes(new, old, start_row=2) == [
        'вкладка «Лист», колонка A: появился заголовок «Артикул» (используется как «code»)',
    ]


def test_sheet_renamed_and_removed() -> None:
    """переименование вкладки и её пропажа."""
    old = _head(('Артикул', None, 'Название'), name='Шины')
    renamed = _head(('Артикул', None, 'Название'), name='Шины НСК')
    empty = FileHead(sheets=(SheetHead('Другая', ()),))

    assert _changes(old, renamed, start_row=2) == ['вкладка №1 переименована: «Шины» → «Шины НСК»']
    no_sheet = _schema(FileHead(sheets=()), 2)
    old_schema = _schema(old, 2)
    assert compare_schemas(old_schema, no_sheet, _COLUMNS) == ['вкладка №1 «Шины» пропала из файла']
    assert _changes(old, empty, start_row=2)[0].startswith('вкладка №1 переименована')


def test_json_missing_key() -> None:
    """пропавшее используемое json-поле называется вместе с полем модели."""
    columns: dict[int | str, str] = {'article': 'code', 'name': 'title'}
    old = _json_schema(['article', 'name', 'x'], columns)
    new = _json_schema(['name', 'x'], columns)

    assert compare_schemas(old, new, columns) == ['в данных больше нет поля «article» (используется как «code»)']


def _json_schema(keys: list[str], columns: dict[int | str, str]) -> PriceSchema:
    head = FileHead(json_keys=frozenset(keys))
    return build_schema(head, start_row=0, sheet_indexes=(), columns=columns)


def test_read_file_head_xlsx_and_json(tmp_path: Path) -> None:
    """чтение шапки реального xlsx и json-файла."""
    book = openpyxl.Workbook()
    sheet = book.active
    assert sheet is not None
    sheet.title = 'Шины'
    sheet.append(['Артикул', 'Цена'])
    sheet.append(['A1', 10])
    book.save(tmp_path / 'price.xlsx')
    records = [{'a': 1}, {'b': 2}, 'junk']
    (tmp_path / 'tire.json').write_text(json.dumps(records), encoding='utf-8')

    xlsx_head = read_file_head(tmp_path / 'price.xlsx')
    json_head = read_file_head(tmp_path / 'tire.json')

    assert xlsx_head.sheets[0].name == 'Шины'
    assert xlsx_head.sheets[0].rows[0] == ('Артикул', 'Цена')
    assert sorted(json_head.json_keys) == ['a', 'b']


@pytest.mark.parametrize('column, label', _EXCEL_COLUMN_CASES)
def test_header_change_names_excel_column(column: int, label: str) -> None:
    """В сообщении о схеме сохраняются буквы колонок, включая границы алфавита."""
    columns: dict[int | str, str] = {column: 'title'}
    padding = (None,) * column
    before = _head((*padding, 'Название'))
    after = _head((*padding, 'Наименование'))
    old = build_schema(before, start_row=2, sheet_indexes=(0,), columns=columns)
    new = build_schema(after, start_row=2, sheet_indexes=(0,), columns=columns)
    expected = f'вкладка «Лист», колонка {label}: заголовок «Название» → «Наименование» (используется как «title»)'
    assert compare_schemas(old, new, columns) == [expected]
