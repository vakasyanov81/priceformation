"""tests for the JSON mode switch"""

import pytest

from infrastructure.logging.json_mode import json_mode_active, quiet_console, set_json_mode


def test_json_mode_off_by_default() -> None:
    """без явного включения консоль пишет"""
    assert not json_mode_active()


def test_set_json_mode_switches_state() -> None:
    """режим включается и выключается вручную"""
    set_json_mode(True)
    assert json_mode_active()

    set_json_mode(False)
    assert not json_mode_active()


def test_quiet_console_restores_state_after_error() -> None:
    """после исключения внутри блока обычный режим возвращается"""
    with pytest.raises(ValueError), quiet_console():
        assert json_mode_active()
        raise ValueError('boom')

    assert not json_mode_active()
