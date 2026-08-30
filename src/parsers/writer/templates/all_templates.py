"""
collection all active templates for writing
"""

from parsers.writer.templates.iwrite_template import IWriteTemplate

from .tmpl.for_drom import ForDrom
from .tmpl.for_inner import ForInner


class UnknownWriterTemplateError(ValueError):
    """Неизвестное имя шаблона записи."""

    def __init__(self, name: str, known: tuple[str, ...]) -> None:
        quoted = repr(name)
        available = ", ".join(known)
        super().__init__(f"Шаблон {quoted} не существует. Доступны: {available}")


def all_writer_templates() -> list[type[IWriteTemplate]]:
    """get all active vendors"""
    return [ForInner, ForDrom]


def writer_template_name(template: type[IWriteTemplate]) -> str:
    """Имя шаблона как в CLI: for_drom, for_inner."""
    return template.__module__.rsplit(".", maxsplit=1)[-1]


def writer_templates_by_name() -> dict[str, type[IWriteTemplate]]:
    """Активные шаблоны записи: имя CLI → класс."""
    return {writer_template_name(template): template for template in all_writer_templates()}


def get_writer_template(name: str) -> type[IWriteTemplate]:
    """Вернуть шаблон по имени CLI или поднять ошибку."""
    templates = writer_templates_by_name()
    template = templates.get(name)
    if template is None:
        raise UnknownWriterTemplateError(name, tuple(templates))
    return template
