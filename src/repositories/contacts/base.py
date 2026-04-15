from __future__ import annotations

import asyncpg


class BaseRepository:
    _conn: asyncpg.Connection | None = None
    _database_url: str | None = None

    @classmethod
    async def connect(cls, dsn: str):
        cls._database_url = dsn
        cls._conn = await asyncpg.connect(dsn)

    @classmethod
    async def disconnect(cls):
        if cls._conn:
            await cls._conn.close()

    @classmethod
    async def execute(cls, query: str, *args):
        assert cls._conn, "Database connection not initialized"
        return await cls._conn.execute(query, *args)

    @classmethod
    async def fetch(cls, query: str, *args):
        assert cls._conn, "Database connection not initialized"
        return await cls._conn.fetch(query, *args)

    @classmethod
    async def fetch_one(cls, query: str, *args):
        assert cls._conn, "Database connection not initialized"
        return await cls._conn.fetchrow(query, *args)