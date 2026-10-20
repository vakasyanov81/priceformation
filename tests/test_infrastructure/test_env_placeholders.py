"""Подстановка переменных окружения в JSON-настройки."""

import pytest

from domain.exceptions import ConfigValidationError
from infrastructure.config.env_placeholders import expand_env

_ENV = {'MAIL_SENDER_STK': 'stk@supplier.ru', 'DOMAIN': 'supplier.ru', 'BLANK': '  '}


def test_placeholders_replaced_in_nested_strings() -> None:
    raw = {'profiles': {'stk': {'sender': '${MAIL_SENDER_STK}', 'port': 993}}, 'list': ['@${DOMAIN}']}

    assert expand_env(raw, _ENV, 'mail.json') == {
        'profiles': {'stk': {'sender': 'stk@supplier.ru', 'port': 993}},
        'list': ['@supplier.ru'],
    }


def test_text_without_placeholders_unchanged() -> None:
    assert expand_env({'subject': 'прайс $5 {x}'}, _ENV, 'mail.json') == {'subject': 'прайс $5 {x}'}


@pytest.mark.parametrize('name', ['NOPE', 'BLANK'])
def test_missing_or_blank_variable_rejected_with_path(name: str) -> None:
    with pytest.raises(ConfigValidationError, match=rf'^mail\.json → items\[0\]: .*«{name}»'):
        expand_env({'items': [f'${{{name}}}']}, _ENV, 'mail.json')
