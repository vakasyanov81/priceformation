"""Строки главного меню: действия, пункт активации поставщиков и сами поставщики."""

from dataclasses import dataclass

from run_dialog.items import MENU_ITEMS, AnswerResult, MenuItem
from services.vendor_activation import VendorState

ACTIVATION_KEY = '4'


@dataclass(frozen=True)
class MenuRow:
    """Строка меню: подпись, шорткат, действие, поставщик или разворачиваемый заголовок."""

    text: str
    shortcut: str = ''
    action: AnswerResult | None = None
    folder: str = ''
    expandable: bool = False


def build_rows(vendors: list[VendorState], *, expanded: bool) -> list[MenuRow]:
    """Строки меню: действия, пункт активации, при развороте — поставщики, затем выход."""
    rows: list[MenuRow] = []
    for menu_item in MENU_ITEMS:
        if menu_item.action is AnswerResult.EXIT:
            rows.append(_activation_row(expanded))
            if expanded:
                rows.extend(_vendor_row(vendor) for vendor in vendors)
        rows.append(_action_row(menu_item))
    return rows


def _action_row(menu_item: MenuItem) -> MenuRow:
    """Строка обычного пункта меню."""
    return MenuRow(f'{menu_item.key} — {menu_item.label}', shortcut=menu_item.key, action=menu_item.action)


def _activation_row(expanded: bool) -> MenuRow:
    """Заголовок пункта активации со стрелкой-индикатором выпадающего списка."""
    mark = '▼' if expanded else '▶'
    return MenuRow(f'{ACTIVATION_KEY} — Активация поставщиков {mark}', shortcut=ACTIVATION_KEY, expandable=True)


def _vendor_row(vendor: VendorState) -> MenuRow:
    """Строка поставщика: [*] активен, [] не активен."""
    mark = '[*]' if vendor.enabled else '[]'
    return MenuRow(f'    {mark} {vendor.name}', folder=vendor.folder)
