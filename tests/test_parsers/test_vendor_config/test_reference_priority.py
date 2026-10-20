"""Очередь поставщиков-эталонов названия из `title.reference_priority`."""

from pathlib import Path

from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.vendor_config.provider import clear_vendor_configs_cache
from parsers.vendor_config.reference_priority import load_reference_priority
from parsers.vendor_config.slot_configs import TitleConfig

_VENDOR = (
    '{{"enabled": 1, "code": "{code}", "name": "{name}", "start_row": 1, "file_templates": ["*.xls"], '
    '"title": {title}, "sections": [{{"name": "{name} (шины)", "columns": {{"1": "title"}}}}]}}'
)


def _write(provider: FakeConfigProvider, stem: str, name: str, title: str) -> None:
    folder = Path(provider.config_file('vendors'))
    folder.mkdir(parents=True, exist_ok=True)
    config = _VENDOR.format(code=stem, name=name, title=title)
    folder.joinpath(f'{stem}.json').write_text(config, encoding='utf-8')


def test_title_reads_reference_priority() -> None:
    """Место в очереди читается; по умолчанию 0 — «не задано»."""
    assert TitleConfig.from_dict({'reference_priority': 3}, 'where').reference_priority == 3
    assert TitleConfig.from_dict({}, 'where').reference_priority == 0


def test_priority_is_set_for_vendor_and_its_sections(fake_config_provider: FakeConfigProvider) -> None:
    """Место поставщика действует и на имя поставщика, и на имена его секций; без места — в карту не попадает."""
    _write(fake_config_provider, 'a', 'Первый', '{"reference_priority": 1}')
    _write(fake_config_provider, 'b', 'Безымянный', '{}')
    clear_vendor_configs_cache()

    assert load_reference_priority() == {'Первый': 1, 'Первый (шины)': 1}
