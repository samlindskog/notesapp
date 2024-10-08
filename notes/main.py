import os
import logging
import uvicorn
from config import config_factory, Resources

logging.basicConfig(level=logging.DEBUG)


async def lifespan(scope, receive, send):
    message = await receive()
    if message["type"] == "lifespan.startup":
        try:
            # loading resources from config
            resources = Resources()
            await resources.current_pool.open(wait=True, timeout=5)
            # initialized repository classes loaded
            scope["state"]["repository"] = resources.repository
            # initialized jinja environment loaded
            scope["state"]["template_env"] = resources.template_env
            # initialized app instance loaded
            scope["state"]["app"] = resources.app()

        except Exception as e:
            await send({"type": "lifespan.startup.failed", "message": str(e)})
        else:
            await send({"type": "lifespan.startup.complete"})
            logging.debug("PROD=" + os.environ["PROD"])

    elif message["type"] == "lifespan.shutdown":
        try:
            pool = scope["state"]["pool"]
            await pool.close()
        except Exception as e:
            await send({"type": "lifespan.shutdown.failed", "message": str(e)})
        else:
            await send({"type": "lifespan.shutdown.complete"})


async def http(scope, recieve, send):
    app = scope["state"]["app"]
    await app.run(scope, recieve, send)


async def app(scope, receive, send):
    match scope["type"]:
        case "http":
            await http(scope, receive, send)
        case "lifespan":
            await lifespan(scope, receive, send)

if __name__ == "__main__":
    prod = os.environ.get("PROD")
    if prod == "true":
        config = config_factory("prod")
    else:
        config = config_factory("dev")
    server = uvicorn.Server(config)
    server.run()
