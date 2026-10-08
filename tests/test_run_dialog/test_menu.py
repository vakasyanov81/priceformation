"""tests for arrow-key navigation menu"""

import contextlib
import sys
from collections.abc import Callable

import pytest

from cfg.color import Colors
from run_dialog import AnswerResult, ask_action, menu, navigation
from run_dialog.items import MENU_ITEMS
from run_dialog.key_codes import Key, KeyPress
from run_dialog.rows import build_rows
from services.vendor_activation import VendorState


class _Tty:
    def isatty(self) -> bool:
        return True


class _NotTty:
    def isatty(self) -> bool:
        return False


def _flip(vendor: VendorState) -> VendorState:
    """Поставщик с перевёрнутым флагом активности."""
    return VendorState(vendor.folder, vendor.name, not vendor.enabled)


def _toggled(vendor: VendorState, folder: str) -> VendorState:
    """Поставщик с перевёрнутым флагом, если совпала папка, иначе без изменений."""
    return _flip(vendor) if vendor.folder == folder else vendor


def _raise_os_error(_folder: str) -> VendorState:
    """Заглушка сервиса: запись конфига падает."""
    raise OSError('disk full')


class _FakeVendorService:
    """Сервис активации в памяти: список и переключение без файлов."""

    def __init__(self, vendors: tuple[VendorState, ...] = ()) -> None:
        self.vendors = list(vendors)

    def list_vendors(self) -> list[VendorState]:
        return list(self.vendors)

    def toggle(self, folder: str) -> VendorState:
        self.vendors = [_toggled(vendor, folder) for vendor in self.vendors]
        return next(vendor for vendor in self.vendors if vendor.folder == folder)


class _StubProvider:
    """ServiceProvider с единственным сервисом активации."""

    def __init__(self, service: _FakeVendorService) -> None:
        self._service = service

    def resolve(self, _interface: object) -> _FakeVendorService:
        return self._service


def _keys(*sequence: Key) -> Callable[[], KeyPress]:
    """read_key из последовательности клавиш без исходного символа."""
    return _presses(*(KeyPress(key) for key in sequence))


def _presses(*sequence: KeyPress) -> Callable[[], KeyPress]:
    """read_key с ограниченным числом нажатий: лишнее чтение падает, а не висит."""
    queue = list(sequence)

    def _next() -> KeyPress:
        if not queue:
            raise AssertionError('меню прочитало больше клавиш, чем задано в тесте')
        return queue.pop(0)

    return _next


@pytest.fixture
def _interactive(monkeypatch: pytest.MonkeyPatch) -> _FakeVendorService:
    """Терминал без реального cbreak и сервис активации в памяти (пустой)."""
    service = _FakeVendorService()
    monkeypatch.setattr(sys, 'stdin', _Tty())
    monkeypatch.setattr(menu, 'raw_terminal', contextlib.nullcontext)
    monkeypatch.setattr(menu, 'ServiceProvider', _StubProvider(service))
    return service


def test_enter_selects_first(_interactive: _FakeVendorService, monkeypatch: pytest.MonkeyPatch) -> None:
    """По умолчанию активен верхний пункт; Enter его возвращает."""
    monkeypatch.setattr(navigation, 'read_key', _keys(Key.ENTER))
    assert ask_action() is MENU_ITEMS[0].action


def test_down_selects_second(_interactive: _FakeVendorService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Стрелка вниз переводит на следующий пункт."""
    monkeypatch.setattr(navigation, 'read_key', _keys(Key.DOWN, Key.ENTER))
    assert ask_action() is MENU_ITEMS[1].action


def test_up_wraps_to_last(_interactive: _FakeVendorService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Стрелка вверх с верхнего пункта зацикливается на последнюю строку (выход)."""
    monkeypatch.setattr(navigation, 'read_key', _keys(Key.UP, Key.ENTER))
    assert ask_action() is AnswerResult.EXIT


def test_down_wraps_around(_interactive: _FakeVendorService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Полный проход вниз возвращает на верхний пункт."""
    rows = build_rows([], expanded=False)
    presses = [Key.DOWN for _row in rows] + [Key.ENTER]
    monkeypatch.setattr(navigation, 'read_key', _keys(*presses))
    assert ask_action() is MENU_ITEMS[0].action


def test_other_key_is_ignored(_interactive: _FakeVendorService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Нераспознанная клавиша не меняет активный пункт."""
    monkeypatch.setattr(navigation, 'read_key', _keys(Key.OTHER, Key.ENTER))
    assert ask_action() is MENU_ITEMS[0].action


def test_exit_key_returns_exit(_interactive: _FakeVendorService, monkeypatch: pytest.MonkeyPatch) -> None:
    """q/Esc выходит из меню."""
    monkeypatch.setattr(navigation, 'read_key', _keys(Key.EXIT))
    assert ask_action() is AnswerResult.EXIT


@pytest.mark.parametrize(
    ('shortcut', 'expected_index'),
    [('1', 0), ('2', 1), ('3', 2)],
)
def test_shortcut_key_selects_item(
    _interactive: _FakeVendorService,
    monkeypatch: pytest.MonkeyPatch,
    shortcut: str,
    expected_index: int,
) -> None:
    """Цифра сразу выбирает соответствующий пункт, без Enter."""
    monkeypatch.setattr(navigation, 'read_key', _presses(KeyPress(Key.OTHER, shortcut)))
    assert ask_action() is MENU_ITEMS[expected_index].action


def test_falls_back_when_not_a_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Не терминал: вместо стрелок вызывается строковый ввод."""
    monkeypatch.setattr(sys, 'stdin', _NotTty())
    called: list[bool] = []

    def _fallback() -> AnswerResult:
        called.append(True)
        return AnswerResult.EXIT

    monkeypatch.setattr(menu, 'ask_by_line', _fallback)
    assert ask_action() is AnswerResult.EXIT
    assert called == [True]


def test_active_item_is_highlighted(
    _interactive: _FakeVendorService,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Активный пункт подсвечивается, выбранный остаётся в выводе без подсветки."""
    monkeypatch.setattr(navigation, 'read_key', _keys(Key.DOWN, Key.ENTER))
    ask_action()
    out = capsys.readouterr().out
    assert 'Выберите действие' in out
    assert f'{Colors.REVERSE}{MENU_ITEMS[1].key}' in out
    assert MENU_ITEMS[1].label in out


def test_activation_shortcut_expands_vendor_list(
    _interactive: _FakeVendorService,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Клавиша 4 разворачивает список поставщиков с маркером [] / [*]."""
    _interactive.vendors = [VendorState('stk', 'STK', False), VendorState('mim', 'Мим', True)]
    keys = [KeyPress(Key.OTHER, '4'), KeyPress(Key.EXIT)]
    monkeypatch.setattr(navigation, 'read_key', _presses(*keys))

    assert ask_action() is AnswerResult.EXIT

    out = capsys.readouterr().out
    assert '    [] STK' in out
    assert '    [*] Мим' in out


def test_enter_on_vendor_toggles_it(
    _interactive: _FakeVendorService,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Enter на строке поставщика активирует его; список перерисовывается."""
    _interactive.vendors = [VendorState('stk', 'STK', False)]
    keys = [
        KeyPress(Key.OTHER, '4'),
        KeyPress(Key.DOWN),
        KeyPress(Key.ENTER),
        KeyPress(Key.EXIT),
    ]
    monkeypatch.setattr(navigation, 'read_key', _presses(*keys))

    assert ask_action() is AnswerResult.EXIT

    assert _interactive.vendors[0].enabled is True
    assert '    [*] STK' in capsys.readouterr().out


def test_unknown_shortcut_is_ignored(
    _interactive: _FakeVendorService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Неизвестная цифра не выбирает строку, меню продолжает работу."""
    keys = _presses(KeyPress(Key.OTHER, '9'), KeyPress(Key.ENTER))
    monkeypatch.setattr(navigation, 'read_key', keys)
    assert ask_action() is MENU_ITEMS[0].action


def test_toggle_failure_keeps_menu_alive(
    _interactive: _FakeVendorService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ошибка записи конфига не роняет меню и не меняет флаг."""
    _interactive.vendors = [VendorState('stk', 'STK', False)]
    monkeypatch.setattr(_interactive, 'toggle', _raise_os_error)
    keys = [
        KeyPress(Key.OTHER, '4'),
        KeyPress(Key.DOWN),
        KeyPress(Key.ENTER),
        KeyPress(Key.EXIT),
    ]
    monkeypatch.setattr(navigation, 'read_key', _presses(*keys))

    assert ask_action() is AnswerResult.EXIT
    assert _interactive.vendors[0].enabled is False


def test_enter_on_header_collapses_list(
    _interactive: _FakeVendorService,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Повторный Enter на заголовке сворачивает список."""
    _interactive.vendors = [VendorState('stk', 'STK', False)]
    keys = [
        KeyPress(Key.OTHER, '4'),
        KeyPress(Key.ENTER),
        KeyPress(Key.EXIT),
    ]
    monkeypatch.setattr(navigation, 'read_key', _presses(*keys))

    assert ask_action() is AnswerResult.EXIT

    out = capsys.readouterr().out
    assert 'Активация поставщиков ▼' in out
    assert 'Активация поставщиков ▶' in out


def test_collapse_uses_expanded_frame_height(
    _interactive: _FakeVendorService,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Кадр сворачивания очищается по высоте развёрнутого — без дублей строк."""
    _interactive.vendors = [VendorState('stk', 'STK', True)]
    keys = [
        KeyPress(Key.OTHER, '4'),
        KeyPress(Key.ENTER),
        KeyPress(Key.EXIT),
    ]
    monkeypatch.setattr(navigation, 'read_key', _presses(*keys))

    assert ask_action() is AnswerResult.EXIT

    expanded_height = len(build_rows(_interactive.vendors, expanded=True)) + 1
    assert f'\x1b[{expanded_height}F' in capsys.readouterr().out
