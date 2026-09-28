"""tests for console menu"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from run_dialog import ANSWER_MAP, AnswerResult, ask_action

_INPUT = 'builtins.input'
_PRINT_LOG = 'run_dialog.print_log'
_RETRY_MSG = 'Не понял'
_ACTION_ONE = '1'


def _dialog_input(*answers: str) -> Any:
    """input с ограниченным числом ответов: зациклившийся диалог падает, а не висит."""
    queue = list(answers)

    def _next(_msg: str = '') -> str:
        if not queue:
            raise AssertionError('диалог запросил ответ больше раз, чем их есть в тесте')
        return queue.pop(0)

    return _next


def _log_budget(max_calls: int) -> Any:
    """Ограничитель повторов: while True без input() иначе крутится вечно."""
    calls = {'n': 0}

    def _log(*_args: Any, **_kwargs: Any) -> None:
        calls['n'] += 1
        if calls['n'] > max_calls:
            raise AssertionError('диалог повторяет подсказку бесконечно')

    return _log


def _ask(*answers: str, retries: int = 0) -> Any:
    """Один прогон диалога: ответы, бюджет повторов и перехваченный print_log."""
    log = MagicMock(side_effect=_log_budget(retries))
    with patch(_INPUT, side_effect=_dialog_input(*answers)) as mock_input, patch(_PRINT_LOG, log):
        action = ask_action()
        calls = mock_input.call_count
    return action, calls, log


def test_answer_map_keys() -> None:
    """пункты меню соответствуют ожидаемым действиям"""
    assert ANSWER_MAP['1'] == AnswerResult.MAKE_PRICE_BY_SUPPLIER
    assert ANSWER_MAP['2'] == AnswerResult.UPDATE_ZAPASKA_DATA
    assert ANSWER_MAP['3'] == AnswerResult.REPORT_DOUBLES
    assert ANSWER_MAP['q'] == AnswerResult.EXIT


@pytest.mark.parametrize(
    ('answer', 'expected'),
    [
        ('1', AnswerResult.MAKE_PRICE_BY_SUPPLIER),
        ('2', AnswerResult.UPDATE_ZAPASKA_DATA),
        ('3', AnswerResult.REPORT_DOUBLES),
        ('q', AnswerResult.EXIT),
        ('Q', AnswerResult.EXIT),
        (' q ', AnswerResult.EXIT),
    ],
)
def test_ask_action_returns_action(answer: str, expected: AnswerResult) -> None:
    """Регистр и пробелы не важны: ответ приводится к нижнему регистру и обрезается."""
    action, calls, mock_log = _ask(answer)
    assert action == expected
    assert calls == 1
    assert mock_log.call_count == 0


def test_ask_action_retries_then_answers() -> None:
    """неверный ввод повторяется, затем возвращается действие."""
    action, calls, mock_log = _ask('x', 'y', f'  {_ACTION_ONE} ', retries=2)
    assert action == AnswerResult.MAKE_PRICE_BY_SUPPLIER
    assert calls == 3
    assert mock_log.call_count == 2
    messages = [str(call.args[0]) for call in mock_log.call_args_list]
    assert all(_RETRY_MSG in message for message in messages)


def test_ask_action_menu_lists_every_answer() -> None:
    """В меню перечислены все действия из ANSWER_MAP."""
    seen: list[str] = []

    def _capture(msg: str = '') -> str:
        seen.append(msg)
        return 'q'

    quiet = MagicMock(side_effect=_log_budget(0))
    with patch(_PRINT_LOG, quiet), patch(_INPUT, side_effect=_capture):
        assert ask_action() == AnswerResult.EXIT
    for key in ANSWER_MAP:
        assert key in seen[0]
