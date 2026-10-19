"""tests for MIM API env configuration"""

from typing import Any
from unittest.mock import patch

import pytest

from domain.exceptions import CoreExceptionError
from infrastructure.config.dotenv import load_dotenv
from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.mim_api_config import MimApiConfigError, get_mim_api_config

_TOKEN_ENV = 'MIM_API_TOKEN'
_HOST_ENV = 'MIM_API_HOST'
_TYPES_ENV = 'MIM_API_TYPES'
_TYPES_CASES = [
    ('2', (2,)),
    ('1;2;7', (1, 2, 7)),
    (' 4, 3 ;3 ', (4, 3)),
    ('', (1, 3, 4)),
]
_TO_LOG = 'to_log'
_TEST_SECRET = 'secret'


def test_config_from_dotenv_file(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.delenv(_TOKEN_ENV, raising=False)
    monkeypatch.delenv(_HOST_ENV, raising=False)
    env_file = tmp_path / '.env'
    env_file.write_text(f'{_TOKEN_ENV}={_TEST_SECRET}\n{_HOST_ENV}=host.from.env\n', encoding='utf-8')

    load_dotenv(env_file)
    config = get_mim_api_config()

    assert config.token == _TEST_SECRET
    assert config.host == 'host.from.env'


def test_config_default_host(monkeypatch: Any) -> None:
    monkeypatch.setenv(_TOKEN_ENV, f'  {_TEST_SECRET}  ')
    monkeypatch.delenv(_HOST_ENV, raising=False)

    config = get_mim_api_config()

    assert config.token == _TEST_SECRET
    assert config.host == 'webmim.svrauto.ru'


def test_types_default(monkeypatch: Any) -> None:
    monkeypatch.setenv(_TOKEN_ENV, _TEST_SECRET)
    monkeypatch.delenv(_TYPES_ENV, raising=False)

    assert get_mim_api_config().types == (1, 3, 4)


@pytest.mark.parametrize(
    ('raw', 'expected'),
    _TYPES_CASES,
)
def test_types_from_env(monkeypatch: Any, raw: str, expected: tuple[int, ...]) -> None:
    monkeypatch.setenv(_TOKEN_ENV, _TEST_SECRET)
    monkeypatch.setenv(_TYPES_ENV, raw)

    assert get_mim_api_config().types == expected


@pytest.mark.parametrize('raw', ['0', '8', 'abc', '1;x', '-1'])
def test_types_invalid(monkeypatch: Any, raw: str) -> None:
    monkeypatch.setenv(_TOKEN_ENV, _TEST_SECRET)
    monkeypatch.setenv(_TYPES_ENV, raw)

    with patch.object(CoreExceptionError, _TO_LOG), pytest.raises(MimApiConfigError, match='неверные категории'):
        get_mim_api_config()


def test_config_blank_host_falls_back_to_default(monkeypatch: Any) -> None:
    monkeypatch.setenv(_TOKEN_ENV, _TEST_SECRET)
    monkeypatch.setenv(_HOST_ENV, '  ')

    assert get_mim_api_config().host == 'webmim.svrauto.ru'


def test_missing_token_with_env_file(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.delenv(_TOKEN_ENV, raising=False)
    (tmp_path / '.env').write_text('OTHER=1\n', encoding='utf-8')

    with (
        patch.object(CoreExceptionError, _TO_LOG),
        patch('infrastructure.config.mim_api_config.load_dotenv', return_value=True),
        pytest.raises(MimApiConfigError, match=_TOKEN_ENV),
    ):
        get_mim_api_config()


def test_missing_token_without_env_file(monkeypatch: Any, fake_config_provider: FakeConfigProvider) -> None:
    monkeypatch.delenv(_TOKEN_ENV, raising=False)

    with (
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(MimApiConfigError, match=r'Не найден файл \.env'),
    ):
        get_mim_api_config()
