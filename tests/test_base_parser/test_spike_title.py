"""tests for spike title helper."""

from domain.row_item.row_item import RowItem
from parsers.base_parser.base_parser_title import get_spike_title


def test_spike_title_empty() -> None:
    assert get_spike_title(RowItem({})) == ''


def test_spike_title_yes() -> None:
    assert get_spike_title(RowItem({'spike': 'да'})) == 'Да'
    assert get_spike_title(RowItem({'spike': 'ш.'})) == 'Да'


def test_spike_title_other() -> None:
    assert get_spike_title(RowItem({'spike': 'нет'})) == ''
