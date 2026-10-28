"""tests for the help action: show README.md on screen"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from app.run_dialog import AnswerResult
from services.help_service import HelpService

_ASK_ACTION = 'app.run.ask_action'
_DOC = '# Документация'


def test_response_show_help() -> None:
    """действие справки выводит README через try_call"""
    with (
        patch(_ASK_ACTION, return_value=AnswerResult.SHOW_HELP),
        patch('app.run.try_call') as mock_try,
    ):
        from app.run import response_processing

        assert response_processing() is True
        mock_try.assert_called_once()
        assert mock_try.call_args.args[0].__name__ == 'run_show_help'


def test_run_show_help(capsys: pytest.CaptureFixture[str]) -> None:
    """вне терминала (пайп/тест) содержимое README.md пишется в stdout"""
    help_service = MagicMock()
    help_service.readme.return_value = _DOC

    with patch(
        'app.run.ServiceProvider.resolve',
        side_effect={HelpService: help_service}.__getitem__,
    ):
        from app.run import run_show_help

        run_show_help()

    help_service.readme.assert_called_once_with()
    assert _DOC in capsys.readouterr().out


def test_run_show_help_pages_in_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    """в терминале справка открывается постраничным просмотрщиком (less/$PAGER)"""
    help_service = MagicMock()
    help_service.readme.return_value = _DOC
    terminal = MagicMock()
    terminal.isatty.return_value = True
    monkeypatch.setattr(sys, 'stdout', terminal)

    with (
        patch(
            'app.run.ServiceProvider.resolve',
            side_effect={HelpService: help_service}.__getitem__,
        ),
        patch('app.run.pydoc.pager') as mock_pager,
    ):
        from app.run import run_show_help

        run_show_help()

        mock_pager.assert_called_once()
        paged = mock_pager.call_args.args[0]
        assert 'Документация' in paged
        assert '\033[' in paged
