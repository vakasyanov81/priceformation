"""Старый формат конфигурации представляет только группу шин и дисков."""

from typing import assert_type

from domain.product_groups import ProductGroup
from parsers.vendor_config.models import TireAndDiskConfig, VendorConfig, VendorSection


def test_legacy_config_exposes_resolved_group() -> None:
    """Группа получает все разрешённые секции и поведение без изменения внешних ключей."""
    config = VendorConfig.from_dict(
        {
            'code': 'demo',
            'name': 'Поставщик',
            'file_templates': ['*.xlsx'],
            'behavior': {'min_rest': 7},
            'sections': [
                {'id': 'tires', 'columns': {'0': 'title'}},
                {'id': 'disks', 'columns': {'1': 'model'}},
            ],
        },
        'demo',
        'demo.json',
    )

    assert_type(config.product_groups, tuple[TireAndDiskConfig])
    assert len(config.product_groups) == 1
    group = config.product_groups[0]
    assert group.id is ProductGroup.TIRE_AND_DISK
    assert group.sections is config.sections
    assert group.behavior is config.behavior
    assert group.behavior.min_rest == 7
    assert [section.id for section in group.sections] == ['tires', 'disks']
    expected_columns = [{0: 'title'}, {1: 'model'}]
    assert [section.columns for section in group.sections] == expected_columns
    assert all(section.product_group is group.id for section in group.sections)


def test_section_group_does_not_depend_on_name() -> None:
    """Отображаемое имя и описание листа не меняют модель настроек секции."""
    section = VendorSection(
        id='demo', name='Аккумуляторы', start_row=1, file_templates=('*.xlsx',), columns={0: 'title'}
    )

    assert section.product_group is ProductGroup.TIRE_AND_DISK
