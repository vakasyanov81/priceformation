"""JSONL-запись по шаблону xlsx."""

import datetime
import json
from pathlib import Path
from typing import Any, ClassVar

from parsers.row_item.row_item import RowItem
from parsers.writer.jsonl_writer import RESULT_META_FILE, write_template_jsonl
from parsers.writer.templates.iwrite_template import IWriteTemplate, WriteColumns
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_inner import ForInner

from .fixtures import FixtureTemplate, write_data

_TITLE = '225/40R18 Crossleader 92Y'
_TYPE_NAME = 'Тип товара'
_PRICE_NAME = 'Цена'


class _RepeatFieldsTemplate(IWriteTemplate):
    """короткие и числовые поля для проверки кодирования повторов."""

    __COLUMNS__: ClassVar[WriteColumns] = [
        {'Номенклатура': {'field': RowItem.title.name}},
        {'Сезон': {'field': RowItem.season.name}},
        {'Шип': {'field': RowItem.spike.name}},
        {'Ширина': {'field': RowItem.width.name}},
        {'Профиль': {'field': RowItem.height_percent.name}},
    ]
    __FILE__ = 'repeat_{now}.xlsx'


class _SkipColumnTemplate(IWriteTemplate):
    """колонка skip не попадает в jsonl."""

    __COLUMNS__: ClassVar[WriteColumns] = [
        {'Номенклатура': {'field': RowItem.title.name}},
        {'Скрыто': {'field': RowItem.code.name, 'skip': True}},
    ]
    __FILE__ = 'skip_{now}.xlsx'


class _TitleLastTemplate(IWriteTemplate):
    """title не первая колонка: обход всех колонок обязан дойти до конца."""

    __COLUMNS__: ClassVar[WriteColumns] = [
        {'Сезон': {'field': RowItem.season.name}},
        {'Номенклатура': {'field': RowItem.title.name}},
    ]
    __FILE__ = 'title_last_{now}.xlsx'


class _EmptyDefaultTemplate(IWriteTemplate):
    """колонка с пустым default_value."""

    __COLUMNS__: ClassVar[WriteColumns] = [
        {'Номенклатура': {'field': RowItem.title.name}},
        {'Сезон': {'field': RowItem.season.name, 'default_value': ''}},
    ]
    __FILE__ = 'empty_default_{now}.xlsx'


def _load_meta(folder: Path) -> dict[str, str]:
    loaded = json.loads((folder / RESULT_META_FILE).read_text(encoding='utf-8'))
    columns: dict[str, str] = {}
    for key, column_name in loaded.items():
        if not str(key).isdigit():
            continue
        columns[str(key)] = str(column_name)
    return columns


def _load_values(folder: Path) -> dict[str, Any]:
    loaded = json.loads((folder / RESULT_META_FILE).read_text(encoding='utf-8'))
    raw = loaded.get('values', {})
    assert isinstance(raw, dict)
    return raw


def _first_row(path: str) -> dict[str, Any]:
    text = Path(path).read_text(encoding='utf-8')
    loaded = json.loads(text.splitlines()[0])
    assert isinstance(loaded, dict)
    return loaded


def _meta_key(meta: dict[str, str], column: str) -> str:
    for key, name in meta.items():
        if name == column:
            return key
    raise AssertionError(column)


def test_write_template_jsonl_rows(tmp_path: Path) -> None:
    """каждая позиция — одна JSON-строка с компактными ключами."""
    path = write_template_jsonl(write_data, FixtureTemplate, str(tmp_path))
    assert path.endswith('default_result.jsonl')
    payload = _first_row(path)
    assert payload == {'1': _TITLE, '2': 3980.0, '3': 4.0}
    assert _load_meta(tmp_path) == {'1': 'Номенклатура', '2': _PRICE_NAME, '3': 'Остаток'}


def test_write_template_jsonl_inner_name(tmp_path: Path) -> None:
    """имя файла как у xlsx, расширение jsonl."""
    path = write_template_jsonl(write_data, ForInner, str(tmp_path))
    assert Path(path).suffix == '.jsonl'
    assert 'price_' in Path(path).name


def test_jsonl_inner_compact_keys(tmp_path: Path) -> None:
    """inner: ключ 1 — тип товара, значения без имён колонок."""
    path = write_template_jsonl(write_data, ForInner, str(tmp_path))
    payload = _first_row(path)
    meta = _load_meta(tmp_path)
    assert meta['1'] == _TYPE_NAME
    assert payload['1'] == 'Автошина'
    assert 'Номенклатура' not in payload


def test_jsonl_shared_keys_across_templates(tmp_path: Path) -> None:
    """колонка с тем же именем получает тот же ключ во всех jsonl папки."""
    inner_path = write_template_jsonl(write_data, ForInner, str(tmp_path))
    drom_path = write_template_jsonl(write_data, ForDrom, str(tmp_path))
    meta = _load_meta(tmp_path)
    inner_row = _first_row(inner_path)
    drom_row = _first_row(drom_path)
    type_key = _meta_key(meta, _TYPE_NAME)
    price_key = _meta_key(meta, _PRICE_NAME)
    assert inner_row[type_key] == drom_row[type_key] == 'Автошина'
    assert inner_row[price_key] == drom_row[price_key] == 3980.0
    assert meta['1'] == _TYPE_NAME


def test_jsonl_drom_skips_empty_rest(tmp_path: Path) -> None:
    """exclude шаблона drom отбрасывает пустой остаток."""
    empty_rest: dict[str, Any] = {**write_data[0], 'rest_count': None}
    path = write_template_jsonl([empty_rest], ForDrom, str(tmp_path))
    assert Path(path).read_text(encoding='utf-8') == ''
    assert _load_meta(tmp_path)['1'] == _TYPE_NAME


def test_jsonl_skips_skip_columns(tmp_path: Path) -> None:
    """поле skip не пишется в объект и не попадает в мета."""
    path = write_template_jsonl(write_data, _SkipColumnTemplate, str(tmp_path))
    payload = _first_row(path)
    meta = _load_meta(tmp_path)
    assert payload == {'1': _TITLE}
    assert meta == {'1': 'Номенклатура'}
    assert 'Скрыто' not in meta.values()


def test_jsonl_omits_null_columns(tmp_path: Path) -> None:
    """колонка с null не пишется в строку, в мета остаётся."""
    row = {**write_data[0], 'price_markup': None}
    path = write_template_jsonl([row], FixtureTemplate, str(tmp_path))
    assert _first_row(path) == {'1': _TITLE, '3': 4.0}
    assert _load_meta(tmp_path)['2'] == _PRICE_NAME


def test_jsonl_omits_falsy_like_xlsx(tmp_path: Path) -> None:
    """falsy-значение не пишется, как и пустая ячейка xlsx: состав полей один."""
    path = write_template_jsonl(write_data, _EmptyDefaultTemplate, str(tmp_path))
    assert _first_row(path) == {'1': _TITLE}
    assert _load_meta(tmp_path) == {'1': 'Номенклатура', '2': 'Сезон'}


def test_jsonl_omits_empty_string_value(tmp_path: Path) -> None:
    """пустая строка в поле не превращается в ключ с пустым значением."""
    row = {**write_data[0], 'price_recommended': ''}
    path = write_template_jsonl([row], ForInner, str(tmp_path))
    meta = _load_meta(tmp_path)
    assert _meta_key(meta, 'Рекомендуемая Цена') not in _first_row(path)


def test_jsonl_encodes_repeating_values(tmp_path: Path) -> None:
    """повторяющиеся строки кроме title заменяются на @N, числа нет."""
    other = {**write_data[0], 'title': 'other title'}
    path = write_template_jsonl([write_data[0], other], ForInner, str(tmp_path))
    meta = _load_meta(tmp_path)
    type_key = _meta_key(meta, _TYPE_NAME)
    price_key = _meta_key(meta, _PRICE_NAME)
    first_row = _first_row(path)
    assert first_row['1'] == '@1'
    assert first_row[type_key] == '@1'
    assert first_row[price_key] == 3980.0
    codebook = _load_values(tmp_path)
    assert codebook['@1'] == 'Автошина'
    assert 3980.0 not in codebook.values()


def test_jsonl_keeps_unique_values(tmp_path: Path) -> None:
    """строка, встретившаяся один раз, не кодируется."""
    brand = RowItem.manufacturer.name
    first = {**write_data[0], brand: 'BrandA'}
    second = {**write_data[0], 'title': 'other', brand: 'BrandB'}
    path = write_template_jsonl([first, second], ForInner, str(tmp_path))
    brand_key = _meta_key(_load_meta(tmp_path), 'Бренд')
    assert _first_row(path)[brand_key] == 'BrandA'
    assert 'BrandA' not in _load_values(tmp_path).values()


def test_jsonl_reuses_value_codes_across_files(tmp_path: Path) -> None:
    """один и тот же повтор в следующем jsonl получает тот же @N."""
    pair = [write_data[0], {**write_data[0], 'title': 'other'}]
    write_template_jsonl(pair, ForInner, str(tmp_path))
    drom_path = write_template_jsonl(pair, ForDrom, str(tmp_path))
    type_key = _meta_key(_load_meta(tmp_path), _TYPE_NAME)
    drom_row = _first_row(drom_path)
    codebook = _load_values(tmp_path)
    assert drom_row[type_key] == '@1'
    assert codebook['@1'] == 'Автошина'


def _repeat_pair(**fields: Any) -> list[dict[str, Any]]:
    return [
        {**write_data[0], 'title': 't1', **fields},
        {**write_data[0], 'title': 't2', **fields},
    ]


def test_jsonl_skips_code_not_shorter(tmp_path: Path) -> None:
    """@N не ставится, если он не короче исходной строки."""
    path = write_template_jsonl(
        _repeat_pair(season='да', spike='Y'),
        _RepeatFieldsTemplate,
        str(tmp_path),
    )
    meta = _load_meta(tmp_path)
    first = _first_row(path)
    assert first[_meta_key(meta, 'Сезон')] == 'да'
    assert first[_meta_key(meta, 'Шип')] == 'Y'
    assert not _load_values(tmp_path)


def test_jsonl_skips_numeric_strings(tmp_path: Path) -> None:
    """строки-числа, в том числе с точкой, не кодируются."""
    path = write_template_jsonl(
        _repeat_pair(width='225', height_percent='40.5'),
        _RepeatFieldsTemplate,
        str(tmp_path),
    )
    meta = _load_meta(tmp_path)
    first = _first_row(path)
    assert first[_meta_key(meta, 'Ширина')] == '225'
    assert first[_meta_key(meta, 'Профиль')] == '40.5'
    assert not _load_values(tmp_path)


def test_jsonl_encodes_when_code_is_shorter(tmp_path: Path) -> None:
    """повтор длиннее @N по-прежнему сжимается."""
    path = write_template_jsonl(
        _repeat_pair(season='зима'),
        _RepeatFieldsTemplate,
        str(tmp_path),
    )
    season_key = _meta_key(_load_meta(tmp_path), 'Сезон')
    assert _first_row(path)[season_key] == '@1'
    assert _load_values(tmp_path)['@1'] == 'зима'


def test_jsonl_raw_bytes(tmp_path: Path) -> None:
    """Файл jsonl: компактный JSON, кириллица литералом, вложенная папка создаётся."""
    path = write_template_jsonl(write_data, ForInner, str(tmp_path / 'nested' / 'deeper'))
    text = Path(path).read_text(encoding='utf-8')
    assert 'Автошина' in text
    assert 'Мим' in text
    assert '\\u' not in text
    assert '": ' not in text
    assert text.endswith('\n')
    assert text.count('\n') == 1


def test_jsonl_file_name_has_four_digit_year(tmp_path: Path) -> None:
    """В имени файла — четырёхзначный год, а не %y."""
    path = write_template_jsonl(write_data, ForInner, str(tmp_path))
    assert str(datetime.datetime.now().year) in Path(path).name


def test_meta_json_keeps_cyrillic(tmp_path: Path) -> None:
    """result_meta.json: имена колонок кириллицей, а не escape-последовательностями."""
    write_template_jsonl(write_data, FixtureTemplate, str(tmp_path))
    text = (tmp_path / RESULT_META_FILE).read_text(encoding='utf-8')
    assert 'Номенклатура' in text
    assert '\\u' not in text


def _write_meta(folder: Path, payload: dict[str, Any]) -> None:
    (folder / RESULT_META_FILE).write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')


def test_meta_extends_partial_keys(tmp_path: Path) -> None:
    """Новые колонки дописываются после уже известных, нечисловые ключи мета выбрасываются."""
    _write_meta(tmp_path, {'note': 'ручной', '1': 'Номенклатура'})
    path = write_template_jsonl(write_data, FixtureTemplate, str(tmp_path))
    assert _first_row(path) == {'1': _TITLE, '2': 3980.0, '3': 4.0}
    assert _load_meta(tmp_path) == {'1': 'Номенклатура', '2': _PRICE_NAME, '3': 'Остаток'}


def test_meta_keeps_key_order_of_existing_meta(tmp_path: Path) -> None:
    """Нечисловые ключи в начале мета пропускаются, а не обрывают разбор."""
    _write_meta(
        tmp_path,
        {'values': {}, 'note': 1, '1': 'Остаток', '2': _PRICE_NAME, '3': 'Номенклатура'},
    )
    path = write_template_jsonl(write_data, FixtureTemplate, str(tmp_path))
    assert _first_row(path) == {'1': 4.0, '2': 3980.0, '3': _TITLE}


def test_meta_drops_unusable_stored_codes(tmp_path: Path) -> None:
    """Код, не короче значения, из мета не переиспользуется."""
    _write_meta(tmp_path, {'values': {'@1': 'да'}})
    path = write_template_jsonl(_repeat_pair(season='да'), _RepeatFieldsTemplate, str(tmp_path))
    season_key = _meta_key(_load_meta(tmp_path), 'Сезон')
    assert _first_row(path)[season_key] == 'да'
    assert not _load_values(tmp_path)


def test_meta_reuses_stored_code_index(tmp_path: Path) -> None:
    """Новый код продолжает нумерацию сохранённой, а не начинается с @1."""
    _write_meta(tmp_path, {'values': {'@1': 'Автошина', '@2': 'Зимняя', '@3': '225'}})
    path = write_template_jsonl(_repeat_pair(season='Зимняя'), _RepeatFieldsTemplate, str(tmp_path))
    season_key = _meta_key(_load_meta(tmp_path), 'Сезон')
    assert _first_row(path)[season_key] == '@2'
    assert _load_values(tmp_path) == {'@1': 'Автошина', '@2': 'Зимняя'}


def test_meta_drops_values_without_codes(tmp_path: Path) -> None:
    """Непригодные сохранённые коды вычищаются из мета, а не висят вечно."""
    _write_meta(tmp_path, {'values': {'@1': '225'}})
    path = write_template_jsonl(_repeat_pair(season='Зимняя'), _RepeatFieldsTemplate, str(tmp_path))
    season_key = _meta_key(_load_meta(tmp_path), 'Сезон')
    assert _first_row(path)[season_key] == '@1'
    assert _load_values(tmp_path) == {'@1': 'Зимняя'}


def test_repeated_title_is_not_coded(tmp_path: Path) -> None:
    """Одинаковый длинный title в строках остаётся текстом: @N ставится только на другие колонки."""
    same = _repeat_pair(season='Зимняя')
    same[0]['title'] = _TITLE
    same[1]['title'] = _TITLE
    path = write_template_jsonl(same, _RepeatFieldsTemplate, str(tmp_path))
    meta = _load_meta(tmp_path)
    first = _first_row(path)
    assert first[_meta_key(meta, 'Номенклатура')] == _TITLE
    assert first[_meta_key(meta, 'Сезон')] == '@1'
    assert _load_values(tmp_path) == {'@1': 'Зимняя'}


def test_repeated_title_is_not_coded_when_title_is_last(tmp_path: Path) -> None:
    """title в последней колонке тоже не кодируется: обход идёт до конца списка."""
    same = _repeat_pair(season='Зимняя')
    same[0]['title'] = _TITLE
    same[1]['title'] = _TITLE
    path = write_template_jsonl(same, _TitleLastTemplate, str(tmp_path))
    meta = _load_meta(tmp_path)
    first = _first_row(path)
    assert first[_meta_key(meta, 'Номенклатура')] == _TITLE
    assert first[_meta_key(meta, 'Сезон')] == '@1'
    assert _load_values(tmp_path) == {'@1': 'Зимняя'}
