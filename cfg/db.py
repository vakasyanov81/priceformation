# -*- coding: utf-8 -*-
"""
configuration for database
"""
__author__ = "Kasyanov V.A."

import os
from typing import NamedTuple


class DBConfig(NamedTuple):
    host: str
    port: str
    user_name: str
    password: str
    db_name: str


def get_config() -> DBConfig:
    """get db configuration"""
    from .main import __FILE_PRICES__, __PROJECT_ROOT__

    return DBConfig(
        **{
            "host": "localhost",
            "port": 5433,
            "user_name": "postgres",
            "password": "postgres",
            "db_name": __PROJECT_ROOT__
            + os.sep
            + __FILE_PRICES__
            + os.sep
            + "price_formation.db",
        }
    )
