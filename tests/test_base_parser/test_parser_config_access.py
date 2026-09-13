"""tests for ParserConfigAccess helpers and edge cases."""

import pytest

from parsers.base_parser.base_parser import BaseParser
from parsers.base_parser.base_parser_access import ParseConfigNotSetError


def test_parse_config_not_set_error_message() -> None:
    """ParseConfigNotSetError содержит ожидаемое сообщение."""
    error = ParseConfigNotSetError()
    assert str(error) == "parse_config is not set"


def test_parse_config_raises_without_config() -> None:
    """Вызов parse_config() до set_parse_config — исключение.

    BaseParser.__init__ вызывает repr(self) → parser_params() →
    parse_config() → ParseConfigNotSetError.
    """
    from parsers.base_parser.base_parser_access import ParseConfigNotSetError

    # Прямая проверка исключения через внутренний метод
    error = ParseConfigNotSetError()
    assert str(error) == "parse_config is not set"

    # Проверка, что repr парсера без конфига кидает ошибку
    with pytest.raises(ParseConfigNotSetError):
        BaseParser(parse_config=None)
