import pdb
from contextlib import AbstractAsyncContextManager
from typing import Any
import json
import logging
from psycopg import sql
from psycopg_pool import AsyncConnectionPool


class Repository(AbstractAsyncContextManager):
    # implement tpc transactions
    _xid = None
    _table = ""
    _aconnpool = None

    @classmethod
    def use_async_connection_pool(cls, aconnpool: AsyncConnectionPool):
        cls._aconnpool = aconnpool
        return cls

    async def __aenter__(self):
        assert isinstance(self._aconnpool, AsyncConnectionPool)
        self._aconn = await self._aconnpool.getconn()
        return self

    async def __aexit__(self, exec_type, exec_value, traceback):
        assert isinstance(self._aconnpool, AsyncConnectionPool)
        if exec_type:
            logging.debug("aborting transaction")
            await self._aconn.rollback()
        else:
            logging.debug("commiting transaction")
            await self._aconn.commit()
        await self._aconnpool.putconn(self._aconn)

    """
    Filter repository by column = value. Optionally specify orderby, record limit, offset,
    DESC of ASC, and encoding
    """

    async def queryfilter(
        self,
        column: str,
        value: str,
        orderby: str = "",
        limit: int = 15,
        offset: int = 0,
        desc: bool = True,
        encoding: None | str = "utf-8",
    ) -> dict[str, Any] | bytes:
        _desc = desc and "DESC" or "ASC"

        query = sql.SQL(
            """
            SELECT * FROM notes.{tableref1} WHERE {colref1} = %s
            ORDER BY {colref2} """
            + _desc
            + """ LIMIT %s OFFSET %s
            """
        ).format(
            tableref1=sql.Identifier(self._table),
            colref1=sql.Identifier(column),
            colref2=sql.Identifier(orderby),
        )
        async with self._aconn.cursor() as acur:
            logging.debug("executing query: " + query.as_string(None))
            await acur.execute(query, (value, limit, offset))
            query_response = await acur.fetchall()
        if not encoding:
            return query_response
        else:
            return json.dumps(query_response).encode(encoding)

    async def insert(
        self,
        columns: list[str],
        values: list[str],
        returning: bool = False,
        encoding: str = "utf-8",
    ) -> dict[str, Any] | bytes | None:
        _returning = returning and "RETURNING *" or ""

        query = sql.SQL(
            """
            INSERT INTO notes.{tableref1} ({colrefs1}) VALUES ({placeholders})
            """
            + _returning
        ).format(
            tableref1=sql.Identifier(self._table),
            colrefs1=sql.SQL(", ").join(sql.Identifier(n) for n in columns),
            placeholders=sql.SQL(", ").join(sql.Placeholder() * len(columns)),
        )
        async with self._aconn.cursor() as acur:
            logging.debug("executing query: " + query.as_string(None))
            await acur.execute(query, values)
            query_response = await acur.fetchone()
        if returning and not encoding:
            return query_response
        else:
            return json.dumps(query_response).encode(encoding)

    async def delete(self, column: str, value: str) -> None:
        query = sql.SQL(
            """
            DELETE FROM notes.{tableref} WHERE {colref} = %s
            """
        ).format(
            tableref=sql.Identifier(self._table),
            colref=sql.Identifier(column),
        )
        async with self._aconn.cursor() as acur:
            logging.debug("executing query: " + query.as_string(None))
            await acur.execute(query, value)


class AssetsRepository(Repository):
    _table = "assets"


class ProfilesRepository(Repository):
    _table = "profiles"
