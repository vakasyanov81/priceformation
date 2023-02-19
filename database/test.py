import sqlite3

from cfg.main import get_config

try:
    cfg = get_config()
    sqlite_connection = sqlite3.connect(cfg.db().db_name)
    cursor = sqlite_connection.cursor()

    sqlite_select_query = "select sqlite_version();"
    cursor.execute(sqlite_select_query)
    record = cursor.fetchall()
    cursor.close()

except sqlite3.Error:
    pass
finally:
    if sqlite_connection:
        sqlite_connection.close()
