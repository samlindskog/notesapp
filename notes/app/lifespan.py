import logging

from psycopg_pool import (AsyncConnectionPool)
from config import (async_pool_config)

applogger = logging.getLogger("app")

async def lifespan(scope, receive, send):
    message = await receive()
    if message["type"] == "lifespan.startup":
        try:
            aconnpool = AsyncConnectionPool(**async_pool_config)
            await aconnpool.open(wait = True, timeout = 30)
            scope["state"] = {"aconnpool": aconnpool}
        except Exception:
            await send({
                "type": "lifespan.startup.failed",
                "message": Exception
            })
        else:
            await send({"type": "lifespan.startup.complete"})

    elif message["type"] == "lifespan.shutdown":
        try:
            aconnpool = scope["state"]["aconnpool"]
            aconnpool.close()
        except Exception:
            await send({
                "type": "lifespan.shutdown.failed",
                "message": Exception
            })
        else:
            await send({
                "type": "lifespan.shutdown.complete"
            })
        

    scope["state"] = {
        "async_conn_pool": AsyncConnectionPool(**async_pool_config),
    }
