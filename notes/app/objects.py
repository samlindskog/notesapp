from contextlib import AbstractAsyncContextManager
import logging
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)

class Repository(AbstractAsyncContextManager):
    _aconnpool = None

    @classmethod
    def use_async_connection_pool(cls, aconnpool: AsyncConnectionPool):
        cls._aconnpool = aconnpool
        return cls

    async def __aenter__(self):
        assert isinstance(self._aconnpool, AsyncConnectionPool)
        self._aconn = await self._aconnpool.getconn()
        return self._aconn

    async def __aexit__(self, exec_type, exec_value, traceback):
        assert isinstance(self._aconnpool, AsyncConnectionPool)
        if exec_type:
            logger.debug("aborting transaction")
            await self._aconn.rollback()
        else:
            logger.debug("commiting transaction")
            await self._aconn.commit()
        await self._aconnpool.putconn(self._aconn)

