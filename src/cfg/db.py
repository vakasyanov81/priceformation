# -*- coding: utf-8 -*-
"""
configuration for database
"""
__author__ = "Kasyanov V.A."

from typing import NamedTuple


# pylint: disable=too-many-class-parents
class DBConfig(NamedTuple):
    """database configuration container"""

    host: str
    port: str
    user_name: str
    password: str
    db_name: str


def get_config(project_root) -> DBConfig:
    """get db configuration"""

    return DBConfig(
        **{
            "host": "localhost",
            "port": 5433,
            "user_name": "postgres",
            "password": "postgres",
            "db_name": f"{project_root}/db.sqlite3",
        }
    )
