"""Контракты прямого разбора шинной секции и контекст её диагностики."""

import pytest

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.models import VendorConfig
from parsers.vendor_config.section_models import VendorSection
from parsers.vendor_config.section_selector import SectionSelector

_WHERE = 'demo.json → product_groups[0] → sections[0]'


def _section(raw: object) -> VendorSection:
    vendor = VendorConfig(folder='demo', code='demo', name='Поставщик')
    inherited = {'file_templates': ['*.xlsx'], 'columns': {'0': 'title'}}
    return VendorSection.from_dict(raw, _WHERE, vendor, inherited)


@pytest.mark.parametrize(
    'raw',
    [
        [],
        {'id': 'tire', 'file_templates': 42},
        {'id': 'tire', 'columns': 42},
        {'id': 42},
        {'id': 'tire', 'start_row': 'x'},
        {'id': 'tire', 'category': []},
        {'id': 'tire', 'category': {'unknown_skip': 'x'}},
        {'id': 'tire', 'title': []},
        {'id': 'tire', 'title': {'aliases': 42}},
        {'id': 'tire', 'pricing': []},
        {'id': 'tire', 'pricing': {'policy': 42}},
        {'id': 'tire', 'behavior': []},
        {'id': 'tire', 'behavior': {'min_rest': 'x'}},
        {'id': 'tire', 'row_selector': {}},
        {'id': 'tire', 'section_selector': {}},
    ],
)
def test_direct_section_error_preserves_source_path(raw: object) -> None:
    """Публичный from_dict сохраняет источник и без предварительной проверки VendorConfig."""
    with pytest.raises(ConfigValidationError) as caught:
        _section(raw)

    assert str(caught.value).startswith(_WHERE)


def test_section_keeps_root_selector_and_config_path() -> None:
    """Секция сохраняет селектор раздела и адрес для дальнейшей маршрутизации."""
    section = _section({'id': 'tire', 'section_selector': {'column': '0', 'keywords': ['Шины']}})

    assert section.section_selector == SectionSelector('0', ('шины',))
    assert section.config_path == _WHERE


def test_missing_templates_has_section_diagnostic() -> None:
    """Отсутствие шаблонов объясняется на уровне секции, как и пустой итоговый список."""
    vendor = VendorConfig(folder='demo', code='demo', name='Поставщик')
    with pytest.raises(ConfigValidationError) as caught:
        VendorSection.from_dict({'id': 'tire'}, _WHERE, vendor, {'columns': {'0': 'title'}})

    assert str(caught.value) == f'{_WHERE}: не задан «file_templates»: ни в секции, ни у поставщика'
