import uvicorn

import config as c
from responses import (rstart404, rbody)
import latex

async def app(scope, receive, send):
    print(scope)
    assert scope['type'] == 'http'
    url = scope['raw_path'].decode('utf-8')

    match url:
        case '/users':
            pass
        case '/articles':
            pass
        case '/assets':
            await latex.test_site(send)
        case _:
            await send(rstart404.r)
            await send(rbody.r(f"Error 404: URL {url} not found".encode('utf-8')))


if __name__ == "__main__":
    config = c.config_factory('development')
    server = uvicorn.Server(config)
    server.run()
