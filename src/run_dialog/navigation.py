"""Навигация по главному меню и разворот списка поставщиков."""

from dataclasses import dataclass

from domain.exceptions import ConfigValidationError
from run_dialog.items import AnswerResult
from run_dialog.key_codes import Key, KeyPress
from run_dialog.keys import read_key
from run_dialog.rows import MenuRow, build_rows
from run_dialog.screen import draw, settle
from services.vendor_activation import VendorActivationService

_STEPS = {Key.UP: -1, Key.DOWN: 1}


@dataclass
class MenuView:
    """Состояние экрана меню: сервис, строки, активная строка, разворот и высота кадра."""

    service: VendorActivationService
    rows: list[MenuRow]
    active: int = 0
    expanded: bool = False
    height: int = 0

    def redraw(self) -> None:
        """Перерисовать меню поверх прошлого кадра и запомнить новую высоту."""
        self.height = draw(self.rows, self.active, previous=self.height)

    def finish(self) -> None:
        """Стереть кадр, оставив выбранную строку."""
        settle(self.rows, self.active, previous=self.height)


def navigate(view: MenuView) -> AnswerResult:
    """Крутить ввод, пока не выбрано действие или выход."""
    while True:
        action = _handle_press(view, read_key())
        if action is not None:
            view.finish()
            return action


def _handle_press(view: MenuView, press: KeyPress) -> AnswerResult | None:
    """Разобрать нажатие: движение по строкам, выбор строки или выход."""
    if press.key is Key.EXIT:
        return AnswerResult.EXIT
    if press.key in _STEPS:
        step = _STEPS.get(press.key, 0)
        view.active = (view.active + step) % len(view.rows)
    elif press.key is Key.ENTER:
        return _commit(view)
    else:
        shortcut = _shortcut_index(view.rows, press.char)
        if shortcut is not None:
            view.active = shortcut
            return _commit(view)
    view.redraw()
    return None


def _commit(view: MenuView) -> AnswerResult | None:
    """Выбрать активную строку: действие, разворот списка или переключение поставщика."""
    row = view.rows[view.active]
    if row.action is not None:
        return row.action
    if row.expandable:
        view.expanded = not view.expanded
    if row.folder:
        _toggle(view.service, row.folder)
    view.rows = build_rows(view.service.list_vendors(), expanded=view.expanded)
    view.redraw()
    return None


def _toggle(service: VendorActivationService, folder: str) -> None:
    """Переключить поставщика; ошибку записи не роняем — маркер просто не изменится."""
    try:
        service.toggle(folder)
    except (OSError, ConfigValidationError):
        return


def _shortcut_index(rows: list[MenuRow], char: str) -> int | None:
    """Индекс строки по горячей клавише, если она известна."""
    if not char:
        return None
    for index, row in enumerate(rows):
        if row.shortcut == char:
            return index
    return None
