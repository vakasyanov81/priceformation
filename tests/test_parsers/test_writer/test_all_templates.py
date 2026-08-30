"""tests for writer templates collection"""

import pytest

from parsers.writer.templates.all_templates import (
    UnknownWriterTemplateError,
    all_writer_templates,
    get_writer_template,
    writer_template_name,
    writer_templates_by_name,
)
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_inner import ForInner


def test_all_writer_templates_order() -> None:
    """активные шаблоны: внутренний и drom"""
    assert all_writer_templates() == [ForInner, ForDrom]


def test_writer_template_cli_names() -> None:
    """имена CLI совпадают с модулями шаблонов."""
    names = writer_templates_by_name()
    assert names == {"for_inner": ForInner, "for_drom": ForDrom}
    assert writer_template_name(ForDrom) == "for_drom"


def test_get_writer_template_known() -> None:
    """известное имя возвращает класс шаблона."""
    assert get_writer_template("for_drom") is ForDrom


def test_get_writer_template_unknown() -> None:
    """неизвестное имя — ошибка со списком доступных."""
    with pytest.raises(UnknownWriterTemplateError, match="nope") as error:
        get_writer_template("nope")
    assert "for_drom" in str(error.value)
    assert "for_inner" in str(error.value)
