"""Разбор типизированной модели parse_config/mail.json."""

import pytest

from domain.exceptions import ConfigValidationError
from parsers.mail.models import DEFAULT_IMAP_FOLDER, DEFAULT_IMAP_HOST, DEFAULT_IMAP_PORT, MailConfig

_MINIMAL_PROFILE = {'sender': 'rmv@pionersib.ru', 'attachment_glob': '*.xlsx'}


def _config(profiles: object) -> MailConfig:
    return MailConfig.from_dict({'profiles': profiles}, 'mail.json')


def test_profile_defaults() -> None:
    """Без флагов профиль включён, домен не используется, тема не фильтруется."""
    profile = _config({'pioner': _MINIMAL_PROFILE}).profiles['pioner']
    assert profile.sender == 'rmv@pionersib.ru'
    assert profile.attachment_glob == '*.xlsx'
    assert profile.sender_is_domain is False
    assert profile.subject_keyword is None
    assert profile.enabled is True


def test_profile_explicit_flags() -> None:
    """sender_is_domain=1 и subject_keyword читаются из конфига."""
    raw = {
        'sender': 'nortec-tyres.ru',
        'sender_is_domain': 1,
        'subject_keyword': 'прайс',
        'attachment_glob': 'прайс*.xlsx',
    }
    profile = _config({'poshk': raw}).profiles['poshk']
    assert profile.sender_is_domain is True
    assert profile.subject_keyword == 'прайс'


def test_disabled_profile_excluded() -> None:
    """Профиль с enabled=0 не попадает в enabled_profiles."""
    raw = {**_MINIMAL_PROFILE, 'enabled': 0}
    config = _config({'stk': raw, 'pioner': _MINIMAL_PROFILE})
    assert config.enabled_profiles() == {'pioner': config.profiles['pioner']}


def test_account_defaults_when_imap_absent() -> None:
    """Без секции imap берутся значения по умолчанию."""
    account = MailConfig.from_dict({'profiles': {}}, 'mail.json').account
    assert account.host == DEFAULT_IMAP_HOST
    assert account.port == DEFAULT_IMAP_PORT
    assert account.folder == DEFAULT_IMAP_FOLDER


def test_account_override() -> None:
    """Секция imap переопределяет host, port и folder."""
    raw = {'imap': {'host': 'imap.example.ru', 'port': 143, 'folder': 'Prices'}, 'profiles': {}}
    account = MailConfig.from_dict(raw, 'mail.json').account
    assert account.host == 'imap.example.ru'
    assert account.port == 143
    assert account.folder == 'Prices'


def test_missing_profiles_section_gives_empty() -> None:
    """Без секции profiles список профилей пуст."""
    assert MailConfig.from_dict({'imap': {}}, 'mail.json').profiles == {}


@pytest.mark.parametrize(
    'raw',
    [
        {'attachment_glob': '*.xlsx'},
        {'sender': 'a@b.ru'},
        {'sender': 'a@b.ru', 'attachment_glob': 5},
    ],
)
def test_invalid_profile(raw: dict[str, object]) -> None:
    """Отсутствующие или неверные поля профиля — ошибка конфига."""
    with pytest.raises(ConfigValidationError):
        _config({'pioner': raw})


def test_invalid_sender_is_domain_flag() -> None:
    """sender_is_domain принимает только 0/1."""
    raw = {**_MINIMAL_PROFILE, 'sender_is_domain': 2}
    with pytest.raises(ConfigValidationError, match='sender_is_domain'):
        _config({'pioner': raw})


def test_invalid_subject_keyword() -> None:
    """subject_keyword должен быть непустой строкой."""
    raw = {**_MINIMAL_PROFILE, 'subject_keyword': ''}
    with pytest.raises(ConfigValidationError):
        _config({'pioner': raw})


def test_invalid_port() -> None:
    """port должен быть целым."""
    raw = {'imap': {'port': 'imap'}, 'profiles': {}}
    with pytest.raises(ConfigValidationError):
        MailConfig.from_dict(raw, 'mail.json')


def test_profiles_not_object() -> None:
    """profiles должен быть объектом."""
    with pytest.raises(ConfigValidationError, match='profiles'):
        MailConfig.from_dict({'profiles': []}, 'mail.json')


def test_config_not_object() -> None:
    """Корень файла должен быть объектом."""
    with pytest.raises(ConfigValidationError):
        MailConfig.from_dict([], 'mail.json')
