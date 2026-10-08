"""tests for building menu rows with the collapsible vendor list"""

from run_dialog.items import MENU_ITEMS
from run_dialog.rows import build_rows
from services.vendor_activation import VendorState


def _vendors() -> list[VendorState]:
    return [VendorState('stk', 'STK', False), VendorState('mim', 'Мим', True)]


def test_rows_collapsed_hides_vendors() -> None:
    """Свёрнутый список: заголовок со стрелкой ▶, поставщиков нет, выход последний."""
    rows = build_rows(_vendors(), expanded=False)
    texts = [row.text for row in rows]
    assert '4 — Активация поставщиков ▶' in texts
    assert not any('[*]' in text or '[]' in text for text in texts)
    assert rows[-1].action is MENU_ITEMS[-1].action


def test_rows_expanded_lists_vendors_after_header() -> None:
    """Развёрнутый список: заголовок ▼, строки поставщиков между заголовком и выходом."""
    rows = build_rows(_vendors(), expanded=True)
    texts = [row.text for row in rows]
    assert '4 — Активация поставщиков ▼' in texts
    assert '    [] STK' in texts
    assert '    [*] Мим' in texts
    header = next(index for index, row in enumerate(rows) if row.expandable)
    assert rows[header + 1].folder == 'stk'
    assert rows[-1].action is MENU_ITEMS[-1].action


def test_rows_shortcuts() -> None:
    """Шорткаты строк: действия, пункт активации, выход."""
    rows = build_rows([], expanded=False)
    shortcuts = [row.shortcut for row in rows if row.shortcut]
    assert shortcuts == ['1', '2', '3', '4', 'q']
