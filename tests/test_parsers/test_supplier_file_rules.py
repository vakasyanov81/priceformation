"""Контракт планирования имён входных файлов поставщика."""

from pathlib import Path

import pytest

from parsers.supplier_file_rules import SupplierFileRules, plan_files
from parsers.supplier_price.errors import SupplierPriceFileNameError


@pytest.mark.parametrize('extension', ['.xls', '.xlsx'])
def test_plan_files_numbered_name_limit(extension: str) -> None:
    """Последний свободный номер — 99; сотый файл отклоняется без перезаписи."""
    rules = SupplierFileRules((f'price*{extension}',))
    sources = [Path(f'incoming/vendor_{index}{extension}') for index in range(99)]

    planned = plan_files('poshk', rules, sources)

    assert len({price_file.name for price_file in planned}) == len(sources)
    assert planned[-1].source == sources[-1]
    assert planned[-1].name == f'price_99{extension}'
    with pytest.raises(SupplierPriceFileNameError, match=r'vendor_100.*poshk'):
        plan_files('poshk', rules, [*sources, Path(f'incoming/vendor_100{extension}')])


def test_plan_files_preserves_duplicate_context() -> None:
    """Ошибка одинаковых имён называет поставщика и конфликтующее имя."""
    sources = [Path('first/price.xlsx'), Path('second/price.xlsx')]

    with pytest.raises(SupplierPriceFileNameError) as caught:
        plan_files('poshk', SupplierFileRules(('price*.xlsx',)), sources)

    assert str(caught.value) == 'Поставщику «poshk» передано несколько файлов с именем price.xlsx'


def test_plan_files_does_not_rename_json() -> None:
    """JSON сохраняется только при исходном совпадении с маской, без подбора price.json."""
    rules = SupplierFileRules(('price*.json',))
    source = Path('incoming/catalog.json')

    with pytest.raises(SupplierPriceFileNameError) as caught:
        plan_files('zapaska', rules, [source])

    assert str(caught.value) == ('Файл catalog.json не подходит поставщику «zapaska»: разбор читает только price*.json')
