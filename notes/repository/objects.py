from contextlib import AbstractAsyncContextManager
import pdb
import json
import time
import logging
from psycopg import AsyncConnection, sql
from psycopg_pool import AsyncConnectionPool


class Repository(AbstractAsyncContextManager):
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
        assert isinstance(self._aconn, AsyncConnection)
        assert isinstance(self._aconnpool, AsyncConnectionPool)
        if exec_type:
            await self._aconn.rollback()
        else:
            await self._aconn.commit()
        await self._aconnpool.putconn(self._aconn)

    '''
    Filter repository by column = value. Optionally specify orderby, record limit, offset,
    DESC of ASC, and encoding
    '''
    async def queryfilter(self, column: str, value: str, orderby: str = "", limit: int = 15,
                          offset: int = 0, desc: bool = True, encoding: None | str = "utf-8"):
        _desc = desc and "DESC" or "ASC"

        query = sql.SQL('''
            SELECT * FROM notes.{tableref1} WHERE {colref1} = %s
            ORDER BY {colref2} ''' + _desc + ''' LIMIT %s OFFSET %s
            ''').format(
            tableref1=sql.Identifier(self._table),
            colref1=sql.Identifier(column),
            colref2=sql.Identifier(orderby),
        )
        assert isinstance(self._aconn, AsyncConnection)
        async with self._aconn.cursor() as acur:
            await acur.execute(query, (value, limit, offset))
            query_response = await acur.fetchall()
        if not encoding:
            return query_response
        else:
            return json.dumps(query_response).encode(encoding)

    async def insert(self, columns, values, returning=False, encoding: None | str = "utf-8"):
        _returning = returning and "RETURNING *" or ""

        query = sql.SQL('''
            INSERT INTO notes.{tableref1} ({colrefs1}) VALUES ({placeholders})
            ''' + _returning
            ).format(
            tableref1=sql.Identifier(self._table),
            colrefs1=sql.SQL(", ").join(
                sql.Identifier(n) for n in columns
            ),
            placeholders=sql.SQL(", ").join(
                sql.Placeholder() * len(columns)
            )
        )
        async with self._aconn.cursor() as acur:
            await acur.execute(query, values)
            query_response = await acur.fetchone()
        if not encoding:
            return query_response
        else:
            return json.dumps(query_response).encode(encoding)


class AssetsRepository(Repository):
    _table = 'assets'


class ProfilesRepository(Repository):
    _table = 'profiles'
