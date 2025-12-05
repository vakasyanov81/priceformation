"""
collection all active templates for writing
"""

from .tmpl.for_drom import ForDrom
from .tmpl.for_inner import ForInner


def all_writer_templates() -> list:
    """get all active vendors"""
    return [ForInner, ForDrom]
