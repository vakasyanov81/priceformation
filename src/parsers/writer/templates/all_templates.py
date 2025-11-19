# -*- coding: utf-8 -*-
"""
collection all active templates for writing
"""
__author__ = "Kasyanov V.A."

from .tmpl.for_drom import ForDrom
from .tmpl.for_inner import ForInner


def all_writer_templates() -> list:
    """get all active vendors"""
    return [ForInner, ForDrom]
