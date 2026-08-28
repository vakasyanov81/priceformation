"""tests for BaseParser spike title helper."""

from parsers.base_parser.base_parser import BaseParser
from parsers.row_item.row_item import RowItem


def test_spike_title_empty() -> None:
    assert BaseParser.get_spike_title(RowItem({})) == ""


def test_spike_title_yes() -> None:
    assert BaseParser.get_spike_title(RowItem({"spike": "да"})) == "Да"
    assert BaseParser.get_spike_title(RowItem({"spike": "ш."})) == "Да"


def test_spike_title_other() -> None:
    assert BaseParser.get_spike_title(RowItem({"spike": "нет"})) == ""


def test_prepare_title_replaces_comma_in_size() -> None:
    assert BaseParser.prepare_title("31x10,50R15 Mazzini Giantsaver 109S") == "31x10.50R15 Mazzini Giantsaver 109S"
