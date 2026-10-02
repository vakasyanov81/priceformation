"""tests for console menu"""

import logging
from typing import Any
from unittest.mock import patch

import pytest

from run_dialog import ANSWER_MAP, AnswerResult, ask_action

_INPUT = 'builtins.input'
_DIALOG_LOGGER = 'run_dialog'
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


def _retry_messages(caplog: pytest.LogCaptureFixture) -> list[str]:
    """Подсказки диалога, записанные его логгером."""
    caplog.set_level(logging.INFO, logger=_DIALOG_LOGGER)
    return [record.getMessage() for record in caplog.records if record.name == _DIALOG_LOGGER]


def _ask(caplog: pytest.LogCaptureFixture, *answers: str) -> tuple[AnswerResult, int, list[str]]:
    """Один прогон диалога: ответы, число запросов ввода и подсказки."""
    with patch(_INPUT, side_effect=_dialog_input(*answers)) as mock_input:
        action = ask_action()
        calls = mock_input.call_count
    return action, calls, _retry_messages(caplog)


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
def test_ask_action_returns_action(
    caplog: pytest.LogCaptureFixture,
    answer: str,
    expected: AnswerResult,
) -> None:
    """Регистр и пробелы не важны: ответ приводится к нижнему регистру и обрезается."""
    action, calls, retries = _ask(caplog, answer)
    assert action == expected
    assert calls == 1
    assert not retries


def test_ask_action_retries_then_answers(caplog: pytest.LogCaptureFixture) -> None:
    """неверный ввод повторяется, затем возвращается действие."""
    action, calls, retries = _ask(caplog, 'x', 'y', f'  {_ACTION_ONE} ')
    assert action == AnswerResult.MAKE_PRICE_BY_SUPPLIER
    assert calls == 3
    assert len(retries) == 2
    assert all(_RETRY_MSG in message for message in retries)


def test_ask_action_menu_lists_every_answer() -> None:
    """В меню перечислены все действия из ANSWER_MAP."""
    seen: list[str] = []

    def _capture(msg: str = '') -> str:
        seen.append(msg)
        return 'q'

    with patch(_INPUT, side_effect=_capture):
        assert ask_action() == AnswerResult.EXIT
    for key in ANSWER_MAP:
        assert key in seen[0]
