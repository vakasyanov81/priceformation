"""Главное меню приложения: пункты действий и интерактивный ввод."""

from run_dialog.items import ANSWER_MAP as ANSWER_MAP
from run_dialog.items import MENU_ITEMS as MENU_ITEMS
from run_dialog.items import AnswerResult as AnswerResult
from run_dialog.items import MenuItem as MenuItem
from run_dialog.menu import ask_action as ask_action

__ALL__ = ['ANSWER_MAP', 'MENU_ITEMS', 'AnswerResult', 'MenuItem', 'ask_action']
