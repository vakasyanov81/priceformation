"""Тесты сервиса справки: чтение README.md из корня проекта."""

from pathlib import Path

from infrastructure.config.fake_config_provider import FakeConfigProvider
from services.help_service import HelpService


def test_readme_returns_project_documentation(fake_config_provider: FakeConfigProvider) -> None:
    """readme читает README.md из корня проекта."""
    readme = Path(fake_config_provider.project_root) / 'README.md'
    readme.write_text('# Документация\n', encoding='utf-8')

    assert HelpService().readme() == '# Документация\n'
