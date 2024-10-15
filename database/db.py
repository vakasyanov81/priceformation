"""base sqlite3 database logic"""

import asyncio
import json
from collections.abc import Iterable
from typing import Any

import aiosqlite

from cfg.main import get_config


async def get_db() -> aiosqlite.Connection:
    """get database connection"""
    cfg = get_config()
    if not getattr(get_db, "db", None):
        db_ = await aiosqlite.connect(cfg.database().db_name)
        get_db.db_ = db_

    return get_db.db_


async def fetch_all(
    sql: str, params: Iterable[Any] | None = None, *, autocommit: bool = True
) -> list[dict]:
    """fetch all data"""
    cursor = await _get_cursor(sql, params)
    return await get_result(cursor, autocommit)


async def insert(
    sql: str, params: Iterable[Any] | None = None, *, autocommit: bool = True
) -> list[dict]:
    """insert data"""
    db_ = await get_db()
    cursor = await db_.cursor()
    cursor = await cursor.executemany(sql, params)
    return await get_result(cursor, autocommit)


async def get_result(cursor: aiosqlite.Cursor, autocommit: bool) -> list[dict]:
    """get result by cursor"""
    rows = await cursor.fetchall()
    results = []
    for row_ in rows:
        results.append(_get_result_with_column_names(cursor, row_))
    await cursor.close()
    if autocommit:
        await (await get_db()).commit()
    return results


async def fetch_one(
    sql: str, params: Iterable[Any] | None = None, *, autocommit: bool = False
) -> dict | None:
    """fetch one row"""
    cursor = await _get_cursor(sql, params)
    row_ = await cursor.fetchone()
    if not row_:
        return None
    row = _get_result_with_column_names(cursor, row_)
    await cursor.close()
    if autocommit:
        await (await get_db()).commit()
    return row


async def fetch_scalar(sql: str, params: Iterable[Any] | None = None) -> str | None:
    """fetch scalar value"""
    result = await fetch_one(sql, params)
    return list(result.values())[0]


async def fetch_as_dict(sql: str, params: Iterable[Any] | None = None) -> dict | None:
    """fetch result as dict"""
    scalar_json = await fetch_scalar(sql, params)
    scalar = json.loads(scalar_json or "{}")
    result = {}
    if isinstance(scalar, list):
        for i in scalar:
            result.update(i)
    else:
        result = scalar

    return result


async def execute(
    sql: str, params: Iterable[Any] | None = None, *, autocommit: bool = True
) -> None:
    """execute query"""
    db_ = await get_db()
    args: tuple[str, Iterable[Any] | None] = (sql, params)
    await db_.execute(*args)
    if autocommit:
        await db_.commit()


def close_db() -> None:
    """close database connection"""
    asyncio.run(_async_close_db())


async def _async_close_db() -> None:
    """async close database connection"""
    await (await get_db()).close()


async def _get_cursor(sql: str, params: Iterable[Any] | None) -> aiosqlite.Cursor:
    """execute query and get query cursor"""
    db_ = await get_db()
    args: tuple[str, Iterable[Any] | None] = (sql, params)
    cursor = await db_.execute(*args)
    db_.row_factory = aiosqlite.Row
    return cursor


def _get_result_with_column_names(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> dict:
    """get column names with indexes from query cursor"""
    column_names = [d[0] for d in cursor.description]
    resulting_row = {}
    for index, column_name in enumerate(column_names):
        resulting_row[column_name] = row[index]
    return resulting_row
