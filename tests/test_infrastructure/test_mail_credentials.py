"""Учётные данные почты из окружения и интерактивного ввода."""

import getpass
import sys
from pathlib import Path

import pytest

from domain.exceptions import CoreExceptionError
from infrastructure.config import mail_credentials
from infrastructure.config.fake_config_provider import FakeConfigProvider

_LOGIN = 'MAIL_LOGIN'
_PASSWORD = 'MAIL_PASSWORD'
_USER = 'box@example.ru'
_SECRET = 'secret'


class _Tty:
    def isatty(self) -> bool:
        return True


class _NotTty:
    def isatty(self) -> bool:
        return False


@pytest.fixture(autouse=True)
def _clean_mail_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(_LOGIN, raising=False)
    monkeypatch.delenv(_PASSWORD, raising=False)


def test_credentials_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(_LOGIN, _USER)
    monkeypatch.setenv(_PASSWORD, _SECRET)
    assert mail_credentials.get_mail_credentials() == mail_credentials.MailCredentials(login=_USER, password=_SECRET)


def test_credentials_from_dotenv(fake_config_provider: FakeConfigProvider) -> None:
    Path(fake_config_provider.project_root, '.env').write_text(
        f'{_LOGIN}={_USER}\n{_PASSWORD}={_SECRET}\n',
        encoding='utf-8',
    )
    assert mail_credentials.get_mail_credentials() == mail_credentials.MailCredentials(login=_USER, password=_SECRET)


def test_missing_credentials_outside_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    """Вне терминала отсутствие данных — ошибка без зависания на вводе."""
    monkeypatch.setattr(sys, 'stdin', _NotTty())
    with pytest.raises(mail_credentials.MailCredentialsError, match=_LOGIN):
        mail_credentials.get_mail_credentials()


def test_partial_credentials_prompt_password(monkeypatch: pytest.MonkeyPatch) -> None:
    """Если задан только логин, пароль запрашивается интерактивно."""
    monkeypatch.setenv(_LOGIN, _USER)
    monkeypatch.setattr(sys, 'stdin', _Tty())
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: _SECRET)

    assert mail_credentials.get_mail_credentials() == mail_credentials.MailCredentials(login=_USER, password=_SECRET)


def test_prompt_login_and_password(monkeypatch: pytest.MonkeyPatch) -> None:
    """Без окружения и логин, и пароль запрашиваются в диалоге."""
    monkeypatch.setattr(sys, 'stdin', _Tty())
    monkeypatch.setattr('builtins.input', lambda prompt: _USER)
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: _SECRET)

    assert mail_credentials.get_mail_credentials() == mail_credentials.MailCredentials(login=_USER, password=_SECRET)


def test_prompt_empty_is_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Пустой ввод не даёт доступов и приводит к ошибке."""
    monkeypatch.setattr(sys, 'stdin', _Tty())
    monkeypatch.setattr('builtins.input', lambda prompt: '')
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: '')
    with pytest.raises(mail_credentials.MailCredentialsError):
        mail_credentials.get_mail_credentials()


def test_login_input_interrupted(monkeypatch: pytest.MonkeyPatch) -> None:
    """EOF на запросе логина — понятная ошибка доступа."""

    def _raise(_prompt: str) -> str:
        raise EOFError

    monkeypatch.setattr(sys, 'stdin', _Tty())
    monkeypatch.setattr('builtins.input', _raise)
    with pytest.raises(mail_credentials.MailCredentialsError):
        mail_credentials.get_mail_credentials()


def test_password_input_interrupted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Прерывание на запросе пароля — ошибка доступа, а не трейсбек getpass."""
    monkeypatch.setenv(_LOGIN, _USER)

    def _raise(_prompt: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(sys, 'stdin', _Tty())
    monkeypatch.setattr(getpass, 'getpass', _raise)
    with pytest.raises(mail_credentials.MailCredentialsError):
        mail_credentials.get_mail_credentials()


def test_error_is_core_exception() -> None:
    """Ошибка доступов — часть доменной иерархии."""
    assert issubclass(mail_credentials.MailCredentialsError, CoreExceptionError)


_MISSING = (
    'Не заданы учётные данные почты. Укажите MAIL_LOGIN и MAIL_PASSWORD в .env '
    'или введите их в интерактивном режиме.'
)


class _Prompts:
    """Подмена input/getpass: ответы по очереди и журнал приглашений."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, *, login: str = '', password: str = '') -> None:
        self.asked: list[str] = []
        self._login = login
        self._password = password
        monkeypatch.setattr(sys, 'stdin', _Tty())
        monkeypatch.setattr('builtins.input', self._input)
        monkeypatch.setattr(getpass, 'getpass', self._getpass)

    def _input(self, prompt: str) -> str:
        self.asked.append(prompt)
        return self._login

    def _getpass(self, prompt: str) -> str:
        self.asked.append(prompt)
        return self._password


def test_prompts_texts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Приглашения называют, что вводить; ответы обрезаются по краям."""
    prompts = _Prompts(monkeypatch, login=f' {_USER} ', password=f' {_SECRET} ')

    credentials = mail_credentials.get_mail_credentials()

    assert credentials == mail_credentials.MailCredentials(login=_USER, password=_SECRET)
    assert prompts.asked == ['Логин почтового ящика: ', 'Пароль почтового ящика: ']


def test_env_password_prompts_only_login(monkeypatch: pytest.MonkeyPatch) -> None:
    """Пароль из окружения не запрашивается повторно — только логин."""
    monkeypatch.setenv(_PASSWORD, _SECRET)
    prompts = _Prompts(monkeypatch, login=_USER, password='other')

    credentials = mail_credentials.get_mail_credentials()

    assert credentials == mail_credentials.MailCredentials(login=_USER, password=_SECRET)
    assert prompts.asked == ['Логин почтового ящика: ']


@pytest.mark.parametrize(
    ('login', 'password'),
    [(_USER, ''), ('', _SECRET), ('', '')],
    ids=['no-password', 'no-login', 'nothing'],
)
def test_incomplete_input_is_error(monkeypatch: pytest.MonkeyPatch, login: str, password: str) -> None:
    """Без логина или пароля после ввода — ошибка с подсказкой, где их задать."""
    _Prompts(monkeypatch, login=login, password=password)

    with pytest.raises(mail_credentials.MailCredentialsError) as error:
        mail_credentials.get_mail_credentials()

    assert str(error.value) == _MISSING


@pytest.mark.parametrize('interrupt', [EOFError, KeyboardInterrupt], ids=['eof', 'ctrl-c'])
def test_interrupted_prompt_message(monkeypatch: pytest.MonkeyPatch, interrupt: type[BaseException]) -> None:
    """Прерванный ввод логина или пароля — та же ошибка с подсказкой."""

    def _raise(_prompt: str) -> str:
        raise interrupt

    monkeypatch.setattr(sys, 'stdin', _Tty())
    monkeypatch.setattr('builtins.input', _raise)
    with pytest.raises(mail_credentials.MailCredentialsError) as login_error:
        mail_credentials.get_mail_credentials()

    monkeypatch.setenv(_LOGIN, _USER)
    monkeypatch.setattr(getpass, 'getpass', _raise)
    with pytest.raises(mail_credentials.MailCredentialsError) as password_error:
        mail_credentials.get_mail_credentials()

    assert str(login_error.value) == str(password_error.value) == _MISSING


def test_outside_terminal_message(monkeypatch: pytest.MonkeyPatch) -> None:
    """Вне терминала — полный текст подсказки."""
    monkeypatch.setattr(sys, 'stdin', _NotTty())
    with pytest.raises(mail_credentials.MailCredentialsError) as error:
        mail_credentials.get_mail_credentials()

    assert str(error.value) == _MISSING
