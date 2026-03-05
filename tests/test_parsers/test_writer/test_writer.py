"""
tests write price for drom.ru
"""

from unittest.mock import patch, MagicMock

import pytest

from parsers.writer.fake_driver import FakeXlwtDriver
from parsers.writer.xls_writer import XlsWriter, create_result_folder
from .fixtures import FixtureTemplate, write_data


@pytest.mark.parametrize(
    "method, call_count",
    [
        ("parsers.writer.fake_driver.FakeXlwtDriver.add_sheet", 1),
        ("parsers.writer.fake_driver.FakeXlwtDriver.write_head", 1),
        ("parsers.writer.fake_driver.FakeXlwtDriver.write", 3),
        ("parsers.writer.fake_driver.FakeXlwtDriver.save", 1),
    ],
)
@patch("parsers.writer.xls_writer.create_result_folder", MagicMock(return_value=None))
def test_xls_write_call_counts(method, call_count):
    """test write price for drom.ru"""

    with patch(method) as _mock_method:
        fake_driver = FakeXlwtDriver()
        XlsWriter(fake_driver, write_data, template=FixtureTemplate)

    assert _mock_method.call_count == call_count


class TestXlsWriterCreateFolder:
    """Тесты для метода create_folder класса XlsWriter"""

    def test_create_folder_creates_directory(self, tmp_path):
        """
        Проверяет, что метод create_folder создаёт директорию,
        если она отсутствует.
        """

        test_folder = tmp_path / "test_result"

        with patch("parsers.writer.xls_writer.get_result_folder_name") as _patch:
            _patch.return_value = str(test_folder)
            create_result_folder()

        assert test_folder.exists()
        assert test_folder.is_dir()

    def test_create_folder_when_exists_does_not_raise(self, tmp_path):
        """
        Проверяет, что метод create_folder не вызывает ошибок,
        если директория уже существует.
        """

        # Создаём папку заранее
        test_folder = tmp_path / "existing"
        test_folder.mkdir()

        with patch("parsers.writer.xls_writer.get_result_folder_name") as _patch:
            _patch.return_value = str(test_folder)
            create_result_folder()

        # Директория продолжает существовать
        assert test_folder.exists()
