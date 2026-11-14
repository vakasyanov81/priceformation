"""Примеры конфига поставщика plant согласованы между документацией и тестами."""

import json
from pathlib import Path

import pytest


@pytest.mark.parametrize('fixture', ['tasks/examples/plant.json', 'integration_tests/parse_config_example/plant.json'])
def test_plant_config_examples_match_unit_fixture(fixture: str) -> None:
    """Копии примера сохраняют ту же схему и значения, что модульная фикстура."""
    reference = json.loads(Path('tests/parse_config_example/plant.json').read_text())
    assert json.loads(Path(fixture).read_text()) == reference
