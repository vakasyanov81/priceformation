"""Активность поставщика в настройках: выгрузка по API нужна только включённым."""

from __future__ import annotations

import logging

from parsers.vendor_config.provider import load_vendor_configs
from parsers.vendor_config.source import SOURCE_API

logger = logging.getLogger(__name__)


def is_vendor_enabled(folder: str) -> bool:
    """Поставщик включён в настройках; конфига нет — считаем включённым (как раньше)."""
    config = load_vendor_configs().get(folder)
    return True if config is None else bool(config.enabled)


def skip_disabled_upload(folder: str) -> bool:
    """Вернуть True и написать в лог, если поставщик отключён и данные по API грузить не нужно."""
    if is_vendor_enabled(folder):
        return False
    logger.info(f'Поставщик «{folder}» отключён в настройках, данные по API не загружаются.')
    return True


def skip_mail_fetch(folder: str) -> bool:
    """Вернуть True и написать в лог, если прайс поставщика по почте получать не нужно.

    Не нужно, когда поставщик отключён или в настройках выбран разбор по API.
    """
    config = load_vendor_configs().get(folder)
    if config is None:
        return False
    if not config.enabled:
        logger.info(f'Поставщик «{folder}» отключён в настройках, прайс из почты не получается.')
        return True
    if config.source == SOURCE_API:
        logger.info(f'Поставщик «{folder}» работает по API, прайс из почты не получается.')
        return True
    return False
