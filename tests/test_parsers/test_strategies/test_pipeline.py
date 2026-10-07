"""Порядок шагов разбора строки и проверка имён шагов."""

import pytest

from domain.exceptions import ConfigValidationError
from parsers.strategies.pipeline import PIPELINE_STEPS, make_pipeline
from parsers.vendor_config.slot_configs import BehaviorConfig

WHERE = 'pioner.json → behavior'


def test_default_pipeline_keeps_base_order() -> None:
    config = BehaviorConfig()

    assert make_pipeline(config, WHERE) == PIPELINE_STEPS


def test_custom_pipeline_order_kept() -> None:
    steps = ('category', 'min_rest', 'markup', 'title')

    assert make_pipeline(BehaviorConfig(pipeline=steps), WHERE) == steps


def test_unknown_step_raises_with_location() -> None:
    config = BehaviorConfig(pipeline=('title', 'nope'))

    with pytest.raises(ConfigValidationError, match='неизвестный шаг pipeline'):
        make_pipeline(config, WHERE)
