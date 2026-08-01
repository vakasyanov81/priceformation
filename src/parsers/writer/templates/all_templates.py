"""
collection all active templates for writing
"""

from parsers.writer.templates.iwrite_template import IWriteTemplate

from .tmpl.for_drom import ForDrom
from .tmpl.for_inner import ForInner


def all_writer_templates() -> list[type[IWriteTemplate]]:
    """get all active vendors"""
    return [ForInner, ForDrom]
