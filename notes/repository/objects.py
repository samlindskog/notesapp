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
        print("aenter")
        print(time.monotonic())
        assert isinstance(self._aconnpool, AsyncConnectionPool)
        self._aconn = await self._aconnpool.connection().__aenter__()
        return self

    async def __aexit__(self, exec_type, exec_value, traceback):
        print("aexit")
        print(time.monotonic())
        assert isinstance(self._aconn, AsyncConnection)
        await self._aconn.commit()
        await self._aconn.close() #95% sure when in pool, this method on connection acts accordingly

    '''
    Filter repository by column = value. Optionally specify amount and offset,
    default orderby="date" DESC.
    '''
    async def queryfilter(self, column, value, orderby="", limit=15, offset=0, desc=True, utf8_json=True):
        print("queryfilter begin")
        print(time.monotonic())
        _column = column
        _value = value
        _orderby = orderby or column
        _amount = isinstance(limit, int) and limit or ""
        _offset = isinstance(offset, int) and offset or ""
        _desc = desc and "DESC" or "ASC"
        print("generate sql")
        print(time.monotonic())
        
        _query = sql.SQL('''
            SELECT * FROM notes.{tableref1} WHERE {colref1} = %s
            ORDER BY {colref2} ''' + _desc + ''' LIMIT %s OFFSET %s
            ''').format(
                tableref1=sql.Identifier(self._table),
                colref1=sql.Identifier(_column),
                colref2=sql.Identifier(_orderby),
            ) #this is ugly af
        assert isinstance(self._aconn, AsyncConnection)
        async with self._aconn.cursor() as acur:
            await acur.execute(_query, (value, limit, offset))
            query_response = await acur.fetchall()
        if(utf8_json):
            return json.dumps(query_response).encode('utf-8')


class AssetsRepository(Repository):
    _table = 'assets'

class ProfilesRepository(Repository):
    _table = 'profiles'
