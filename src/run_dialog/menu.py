"""Главное меню: навигация стрелками в терминале, ввод строкой в остальных случаях."""

import sys

from run_dialog.items import AnswerResult
from run_dialog.line_fallback import ask_by_line
from run_dialog.navigation import MenuView, navigate
from run_dialog.readers import raw_terminal
from run_dialog.rows import build_rows
from services.service_provider import ServiceProvider
from services.vendor_activation import VendorActivationService


def ask_action() -> AnswerResult:
    """Главное меню: стрелки в терминале, иначе ввод строки."""
    if not sys.stdin.isatty():
        return ask_by_line()
    return _ask_with_arrows()


def _ask_with_arrows() -> AnswerResult:
    """Интерактивное меню с разворотом списка поставщиков."""
    service = ServiceProvider.resolve(VendorActivationService)
    view = MenuView(service, build_rows(service.list_vendors(), expanded=False))
    view.redraw()
    with raw_terminal():
        return navigate(view)
