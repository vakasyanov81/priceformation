# -*- coding: utf-8 -*-
"""
collection all active templates for writing
"""
__author__ = "Kasyanov V.A."

from .for_drom import ForDrom
from .for_inner import ForInner


def all_writer_templates() -> list:
    """get all active vendors"""
    return [ForInner, ForDrom]
