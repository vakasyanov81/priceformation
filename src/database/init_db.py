"""database initialization"""

import os
import traceback
from pathlib import Path
from sqlite3 import DatabaseError

from yoyo import get_backend, read_migrations

from src.cfg import init_cfg
from src.cfg.main import get_config
from src.core.log_message import err_msg, log_msg
from src.database.exception import DBError

cfg = init_cfg()


async def init_db(drop_database=False):
    init_db_sync(drop_database)


def init_db_sync(drop_database=False):
    """database initialization"""
    if Path(get_config().database().db_name).exists() and drop_database:
        Path(get_config().database().db_name).unlink()

    backend = get_backend("sqlite:///" + get_config().database().db_name)
    migrations = read_migrations(cfg.main.project_root + os.sep + "src" + os.sep + "database" + os.sep + "migrations")

    with backend.lock():
        # Apply any outstanding migrations
        try:
            backend.apply_migrations(backend.to_apply(migrations))
        except DatabaseError as _exc:
            err_msg(str(_exc))
            err_msg(traceback.format_exc())
            raise DBError("Ошибка при инициализации базы данных") from _exc
        finally:
            log_msg(
                msg="Миграция базы данных окончена \n",
                need_print_log=True,
                color="green",
            )
