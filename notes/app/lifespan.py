import logging

from psycopg_pool import AsyncConnectionPool
from repository.objects import ProfilesRepository, AssetsRepository
from config import Resources

applogger = logging.getLogger("app")

async def lifespan(scope, receive, send):
    message = await receive()
    if message["type"] == "lifespan.startup":
        try:
            #loading resources from config
            resources = Resources()
            await resources.current_pool.open(wait = True, timeout = 5)
            #initializing shared resources into scope
            scope["state"]["pool"] = resources.current_pool
            scope["state"]["assets"] = resources.assets_class
            scope["state"]["profiles"] = resources.profiles_class
        except Exception:
            await send({
                "type": "lifespan.startup.failed",
                "message": Exception
            })
        else:
            await send({"type": "lifespan.startup.complete"})

    elif message["type"] == "lifespan.shutdown":
        try:
            pool = scope["state"]["pool"]
            await pool.close()
        except Exception:
            await send({
                "type": "lifespan.shutdown.failed",
                "message": Exception
            })
        else:
            await send({
                "type": "lifespan.shutdown.complete"
            })

