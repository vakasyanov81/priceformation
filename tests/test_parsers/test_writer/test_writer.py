"""tests for XlsWriter"""

import importlib
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from parsers.writer import xls_writer as writer_mod
from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.xls_writer import XlsWriter
from parsers.writer.xwlt_driver import XlsxWriterDriver

from .fixtures import FixtureTemplate, write_data


@pytest.mark.parametrize(
    'method, call_count',
    [
        ('parsers.writer.fake_driver.FakeXlwtDriver.add_sheet', 1),
        ('parsers.writer.fake_driver.FakeXlwtDriver.write_head', 1),
        ('parsers.writer.fake_driver.FakeXlwtDriver.write', 3),
        ('parsers.writer.fake_driver.FakeXlwtDriver.save', 1),
    ],
)
def test_xls_write_call_counts(method: Any, call_count: Any, tmp_path: Any) -> None:
    """test write price for drom.ru"""

    with patch(method) as mock_method:
        fake_driver = FakeXlwtDriver()
        XlsWriter(
            fake_driver,
            write_data,
            template=FixtureTemplate,
            result_folder=str(tmp_path),
        ).write()

    assert mock_method.call_count == call_count


def test_constructor_does_not_touch_disk(tmp_path: Any) -> None:
    """конструктор не создаёт папку и не пишет xlsx."""
    result_folder = tmp_path / 'result'
    fake_driver = FakeXlwtDriver()
    XlsWriter(
        fake_driver,
        write_data,
        template=FixtureTemplate,
        result_folder=str(result_folder),
    )
    assert not result_folder.exists()
    assert list(tmp_path.iterdir()) == []
    assert fake_driver.file_name is None
    assert fake_driver.folder is None


def test_write_creates_result_folder(tmp_path: Any) -> None:
    """write создаёт папку результата, если её нет."""
    result_folder = tmp_path / 'result'
    XlsWriter(
        FakeXlwtDriver(),
        write_data,
        template=FixtureTemplate,
        result_folder=str(result_folder),
    ).write()
    assert result_folder.is_dir()


def test_write_when_result_folder_exists(tmp_path: Any) -> None:
    """write не падает, если папка уже есть."""
    result_folder = tmp_path / 'existing'
    result_folder.mkdir()
    XlsWriter(
        FakeXlwtDriver(),
        write_data,
        template=FixtureTemplate,
        result_folder=str(result_folder),
    ).write()
    assert result_folder.is_dir()


def test_write_saves_xlsx_into_result_folder(tmp_path: Any) -> None:
    """write кладёт xlsx в result_folder; без write диск пуст."""
    result_folder = tmp_path / 'out'
    writer = XlsWriter(
        XlsxWriterDriver(),
        write_data,
        template=FixtureTemplate,
        result_folder=str(result_folder),
    )
    assert list(tmp_path.iterdir()) == []
    writer.write()
    saved = result_folder / writer.get_file_name()
    assert saved.is_file()
    assert saved.stat().st_size > 0


def test_xls_writer_result_path(tmp_path: Any) -> None:
    """полный путь к записанному файлу"""
    writer = XlsWriter(
        FakeXlwtDriver(),
        write_data,
        template=FixtureTemplate,
        result_folder=str(tmp_path),
    )
    expected = str((tmp_path / writer.get_file_name()).resolve())
    assert writer.get_result_path() == expected


def test_import_xls_writer_does_not_call_init_cfg(monkeypatch: pytest.MonkeyPatch) -> None:
    """импорт модуля writer не поднимает композиционный корень cfg."""
    spy = MagicMock()
    monkeypatch.setattr('cfg.init_cfg', spy)

    importlib.reload(writer_mod)

    spy.assert_not_called()


def test_get_value_skips_column() -> None:
    """get_value возвращает None для колонки с skip=True."""
    from parsers.writer.xls_writer import get_value

    assert get_value({'Скрытая': {'field': 'title', 'skip': True}}, {}) is None


def test_get_value_returns_list_as_string() -> None:
    """get_value конвертирует список в строку через запятую."""
    from parsers.writer.xls_writer import _to_str

    assert _to_str(['a', '', 'b']) == 'a, b'
    assert _to_str([]) == ''
    assert _to_str(['only']) == 'only'


def test_get_value_falls_back_to_default() -> None:
    """get_value возвращает дефолтное значение, если поля нет."""
    from parsers.writer.xls_writer import get_value

    # default_value 0, поле отсутствует → raw_value = None → None or 0 = 0
    got = get_value({'Цена': {'field': 'price_markup', 'default_value': '0'}}, {})
    assert got == '0'


def test_make_exclude_empty_keeps_all() -> None:
    """make_exclude с пустым exclude возвращает все строки."""
    from parsers.writer.xls_writer import make_exclude

    rows = [{'a': 1}, {'a': 2}]
    assert make_exclude(rows, {}) is rows


def test_get_color_without_map(tmp_path: Any) -> None:
    """_get_color возвращает (None, None), если нет карты цветов."""
    from .fixtures import ColorsWithoutMapTemplate

    fake_driver = FakeXlwtDriver()
    writer = XlsWriter(
        fake_driver,
        write_data,
        template=ColorsWithoutMapTemplate,
        result_folder=str(tmp_path),
    )
    color = writer._get_color(write_data[0])
    assert color == (None, None)


def test_write_row_empty_value_skips(tmp_path: Any) -> None:
    """_write_row пропускает колонки с пустым значением, не падает."""
    from .fixtures import FixtureTemplate

    fake_driver = FakeXlwtDriver()
    XlsWriter(
        fake_driver,
        [{}],
        template=FixtureTemplate,
        result_folder=str(tmp_path),
    ).write()
    assert fake_driver.body == {}  # ничего не записано, но save вызван
