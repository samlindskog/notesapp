from contextlib import AbstractAsyncContextManager
import json
import time
import logging
from psycopg import AsyncConnection, sql
from psycopg_pool import AsyncConnectionPool

class Repository(AbstractAsyncContextManager):
    _table = ""
    _aconnpool = None
    
    @classmethod
    def use_async_connection_pool(cls, aconnpool):
       cls._aconnpool = aconnpool 
       return cls

    async def __aenter__(self):
        assert isinstance(self._aconnpool, AsyncConnectionPool)
        self._aconn = await self._aconnpool.getconn()
        return self

    async def __aexit__(self, exec_type, exec_value, traceback):
        assert isinstance(self._aconn, AsyncConnection)
        assert isinstance(self._aconnpool, AsyncConnectionPool)
        await self._aconn.commit()
        await self._aconnpool.putconn(self._aconn)

    '''
    Filter repository by column = value. Optionally specify orderby, record limit, offset,
    DESC of ASC, and encoding
    '''
    async def queryfilter(self, column, value, orderby="", limit=15, offset=0, desc=True):
        _column = column
        _value = value
        _orderby = orderby or column
        _amount = isinstance(limit, int) and limit or ""
        _offset = isinstance(offset, int) and offset or ""
        _desc = desc and "DESC" or "ASC"
        
        query = sql.SQL('''
            SELECT * FROM notes.{tableref1} WHERE {colref1} = %s
            ORDER BY {colref2} ''' + _desc + ''' LIMIT %s OFFSET %s
            ''').format(
                tableref1=sql.Identifier(self._table),
                colref1=sql.Identifier(_column),
                colref2=sql.Identifier(_orderby),
            ) #this is ugly af
        assert isinstance(self._aconn, AsyncConnection)
        async with self._aconn.cursor() as acur:
            await acur.execute(query, (value, limit, offset))
            query_response = await acur.fetchall()
        return json.dumps(query_response).encode('utf-8')

    async def insert(self, columns, values):
        query = sql.SQL('''
            INSERT INTO notes.{tableref1} ({colrefs1}) VALUES (%s)
                ''').format(
                        tableref1=sql.Identifier(self._table),
                        colrefs1=sql.SQL(", ").join(
                            sql.Identifier(n) for n in columns
                            )
                )
        async with self._aconn as acur:
            await acur.execute(query, values)

class AssetsRepository(Repository):
    _table = 'assets'

class ProfilesRepository(Repository):
    _table = 'profiles'
