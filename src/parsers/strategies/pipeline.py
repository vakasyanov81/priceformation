"""Порядок шагов разбора строки (слот `pipeline`): проверка имён шагов."""

from __future__ import annotations

from domain.exceptions import ConfigValidationError
from parsers.vendor_config.slot_configs import BehaviorConfig

PIPELINE_STEPS = ('title', 'min_rest', 'category', 'markup')
_AVAILABLE = ', '.join(PIPELINE_STEPS)


def make_pipeline(config: BehaviorConfig, where: str) -> tuple[str, ...]:
    """Проверить и вернуть упорядоченные шаги разбора строки."""
    for step in config.pipeline:
        if step not in PIPELINE_STEPS:
            raise ConfigValidationError(
                f'{where}: неизвестный шаг pipeline {step!r} (доступны: {_AVAILABLE})',
            )
    return config.pipeline
