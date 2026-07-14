"""tests for console menu"""

from unittest.mock import patch

from run_dialog import ANSWER_MAP, AnswerResult, ask_action


def test_answer_map_keys():
    """пункты меню соответствуют ожидаемым действиям"""
    assert ANSWER_MAP["1"] == AnswerResult.MAKE_PRICE_BY_SUPPLIER
    assert ANSWER_MAP["2"] == AnswerResult.UPDATE_ZAPASKA_DATA
    assert ANSWER_MAP["q"] == AnswerResult.EXIT


def test_ask_action_retries():
    """неверный ввод повторяется, затем возвращается действие"""
    with (
        patch("builtins.input", side_effect=["x", " 1 "]),
        patch("run_dialog.print_log") as mock_log,
    ):
        assert ask_action() == AnswerResult.MAKE_PRICE_BY_SUPPLIER
        mock_log.assert_called_once()


def test_ask_action_exit():
    """выбор выхода"""
    with patch("builtins.input", return_value="q"):
        assert ask_action() == AnswerResult.EXIT
