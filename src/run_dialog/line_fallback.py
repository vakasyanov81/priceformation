"""Ввод действия строкой, когда stdin не терминал (пайп, перенаправление)."""

import logging

from cfg.color import Colors
from run_dialog.items import ANSWER_MAP, MENU_ITEMS, AnswerResult

logger = logging.getLogger(__name__)


def ask_by_line() -> AnswerResult:
    """Спросить действие цифрой/буквой, повторяя запрос при неверном вводе."""
    prompt = _menu_text()
    while True:
        answer = ANSWER_MAP.get(input(prompt).strip().lower())
        if answer:
            return answer
        logger.info('Не понял, давай ещё раз. \n')


def _menu_text() -> str:
    """Пункты меню одной строкой-подсказкой для input()."""
    lines = '\n'.join(f'{menu_item.key} — {menu_item.label}' for menu_item in MENU_ITEMS)
    return f'{Colors.BOLD}{lines}{Colors.END_COLOR}\n'
