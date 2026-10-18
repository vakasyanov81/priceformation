"""Настройки дублей из parse_config/doubles.json."""

import json
from pathlib import Path

import pytest

from domain.exceptions import ConfigValidationError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.data_provider.doubles_settings import (
    DOUBLES_CONFIG_FILE,
    DoublesSettings,
    load_doubles_settings,
    parse_doubles_settings,
)

_KNOWN = ('for_inner', 'for_drom', 'for_full')


def test_missing_file_excludes_nothing(fake_config_provider: FakeConfigProvider) -> None:
    """Нет doubles.json — дубли не исключаются ни в одном шаблоне."""
    settings = load_doubles_settings(_KNOWN)

    assert settings == DoublesSettings()
    assert not settings.excludes_in('for_drom')


def test_file_is_read(fake_config_provider: FakeConfigProvider) -> None:
    """Шаблоны и приоритетные поставщики читаются из файла настроек."""
    path = Path(fake_config_provider.config_file(DOUBLES_CONFIG_FILE))
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {'exclude_in_templates': ['for_drom'], 'priority_suppliers': [' Автоснабжение ', '']}
    path.write_text(json.dumps(payload), encoding='UTF-8')

    settings = load_doubles_settings(_KNOWN)

    assert settings.excludes_in('for_drom')
    assert not settings.excludes_in('for_inner')
    assert settings.priority_suppliers == ('Автоснабжение',)


def test_unknown_template_names_key_path() -> None:
    """Неизвестный шаблон — ошибка с путём до ключа и списком доступных."""
    with pytest.raises(ConfigValidationError, match=r'exclude_in_templates\[1\].*for_dром.*for_inner'):
        parse_doubles_settings({'exclude_in_templates': ['for_drom', 'for_dром']}, _KNOWN)


def test_not_an_object_is_rejected() -> None:
    """Корень файла — объект."""
    with pytest.raises(ConfigValidationError, match=DOUBLES_CONFIG_FILE):
        parse_doubles_settings(['for_drom'], _KNOWN)


def test_templates_must_be_strings() -> None:
    """Список шаблонов — список строк."""
    with pytest.raises(ConfigValidationError, match='exclude_in_templates'):
        parse_doubles_settings({'exclude_in_templates': 'for_drom'}, _KNOWN)


def test_empty_object_means_no_settings() -> None:
    """Оба ключа необязательны: пустой объект — настройки по умолчанию."""
    assert parse_doubles_settings({}, _KNOWN) == DoublesSettings()


def test_unknown_template_message_lists_all_known_with_comma() -> None:
    """В сообщении — имя файла, путь до ключа, шаблон и все доступные через запятую."""
    expected = (
        f"{DOUBLES_CONFIG_FILE} → exclude_in_templates[0]: шаблон 'x' не существует. "
        'Доступны: for_inner, for_drom, for_full'
    )
    with pytest.raises(ConfigValidationError) as raised:
        parse_doubles_settings({'exclude_in_templates': ['x']}, _KNOWN)
    assert str(raised.value) == expected


@pytest.mark.parametrize('key', ['exclude_in_templates', 'priority_suppliers'])
def test_wrong_type_names_file_and_key(key: str) -> None:
    """Ошибка типа называет файл и ключ."""
    with pytest.raises(ConfigValidationError) as raised:
        parse_doubles_settings({key: 'for_drom'}, _KNOWN)
    assert str(raised.value).startswith(f'{DOUBLES_CONFIG_FILE} → {key}: ожидается список строк')
