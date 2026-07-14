"""tests for writer templates collection"""

from parsers.writer.templates.all_templates import all_writer_templates
from parsers.writer.templates.tmpl.for_drom import ForDrom
from parsers.writer.templates.tmpl.for_inner import ForInner


def test_all_writer_templates_order():
    """активные шаблоны: внутренний и drom"""
    assert all_writer_templates() == [ForInner, ForDrom]
