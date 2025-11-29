# -*- coding: utf-8 -*-
"""
write template for double list
"""
__author__ = "Kasyanov V.A."

from parsers.writer.templates.tmpl.for_inner import ForInner


class Doubles(ForInner):
    """write template for double list"""

    __FILE__ = "double_{now}.xlsx"
