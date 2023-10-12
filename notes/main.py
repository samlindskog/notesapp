import logging
import uvicorn
import snoop
from app.lifespan import lifespan
from app.http import http
from config import config_factory, Resources

logging.basicConfig(level=logging.DEBUG)

async def app(scope, receive, send):
    match scope['type']:
        case 'http':
            await http(scope, receive, send) 
        case 'lifespan':
            await lifespan(scope, receive, send)

if __name__ == "__main__":
    config = config_factory('development')
    server = uvicorn.Server(config)
    server.run()
