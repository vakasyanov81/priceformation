"""tests for writer templates collection"""

import pytest

from parsers.writer.templates.all_templates import (
    UnknownWriterTemplateError,
    all_writer_templates,
    extra_writer_templates,
    get_writer_template,
    writer_template_name,
    writer_templates_by_name,
)
from parsers.writer.templates.iwrite_template import DEFAULT_TEMPLATE_FILE, IWriteTemplate
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_full import ForFull
from parsers.writer.templates.tmpl.for_inner import ForInner
from parsers.writer.xlsx_driver import solid_fill


def test_all_writer_templates_order() -> None:
    """по умолчанию пишутся внутренний и drom, без полного."""
    assert all_writer_templates() == [ForInner, ForDrom]
    assert ForFull not in all_writer_templates()


def test_extra_writer_templates() -> None:
    """полный шаблон доступен только явно."""
    assert extra_writer_templates() == [ForFull]


def test_writer_template_cli_names() -> None:
    """имена CLI совпадают с модулями шаблонов."""
    names = writer_templates_by_name()
    assert names == {'for_inner': ForInner, 'for_drom': ForDrom, 'for_full': ForFull}
    assert writer_template_name(ForDrom) == 'for_drom'
    assert writer_template_name(ForFull) == 'for_full'


def test_get_writer_template_known() -> None:
    """известное имя возвращает класс шаблона."""
    assert get_writer_template('for_drom') is ForDrom
    assert get_writer_template('for_full') is ForFull


def test_get_writer_template_unknown() -> None:
    """неизвестное имя — ошибка со списком доступных."""
    with pytest.raises(UnknownWriterTemplateError, match='nope') as error:
        get_writer_template('nope')
    assert 'for_drom' in str(error.value)
    assert 'for_inner' in str(error.value)
    assert 'for_full' in str(error.value)


def test_get_columns_format_empty_without_format() -> None:
    """get_columns_format возвращает пустой словарь, если нет колонок с format."""

    class _NoFormat(IWriteTemplate):  # noqa: WPS431
        __COLUMNS__ = [{'A': {'field': 'title'}}]  # noqa: RUF012

    no_format = _NoFormat()
    fmt = no_format.get_columns_format()
    assert fmt == {}


def test_misspelled_template_setting_is_not_silently_ignored() -> None:
    """Опечатка в имени настройки ломает чтение, а не молча даёт пустой шаблон.

    С hasattr/getattr опечатка в `__COLUMNS__` давала `[]`, и файл писался без
    колонок. Теперь настройки объявлены в IWriteTemplate, поэтому подкласс без
    них читает то, что задал родитель, а неожиданного имени нет вовсе.
    """

    class _Misspelled(IWriteTemplate):  # noqa: WPS431
        __COLUMN__ = [{'A': {'field': 'title'}}]  # noqa: RUF012

    # Имя есть в классе, но шаблон читает объявленное в IWriteTemplate
    # __COLUMNS__: опечатка не подменяет настройку, а остаётся мёртвым атрибутом.
    assert _Misspelled.__COLUMN__  # noqa: WPS609
    assert _Misspelled().columns() == []
    # Настоящая настройка видна на любом подклассе без hasattr/getattr.
    assert IWriteTemplate.__COLUMNS__ == []
    assert _Misspelled().get_file_name() == DEFAULT_TEMPLATE_FILE


@pytest.mark.parametrize('template', [ForInner, ForDrom, ForFull])
def test_template_colors_are_valid_hex(template: type[IWriteTemplate]) -> None:
    """Цвета шаблонов — валидный #RRGGBB; именованные (blue) роняют запись xlsx."""
    for color in template().colors().get('with_map', {}).values():
        solid_fill(color)  # недопустимый цвет бросит ValueError
