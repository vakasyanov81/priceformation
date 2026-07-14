"""tests for file reader helpers"""

from core.file_reader import read_file, try_read_file


def test_read_file(tmp_path):
    """чтение существующего файла"""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello", encoding="UTF-8")
    assert read_file(str(file_path)) == "hello"


def test_try_read_file_success(tmp_path):
    """try_read_file возвращает содержимое"""
    file_path = tmp_path / "ok.txt"
    file_path.write_text("content", encoding="UTF-8")
    assert try_read_file(str(file_path)) == "content"


def test_try_read_file_missing(tmp_path):
    """отсутствующий файл даёт пустую строку"""
    assert try_read_file(str(tmp_path / "missing.txt")) == ""
