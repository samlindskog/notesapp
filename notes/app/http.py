from app.responses import (rstart404, rbody)
from app.serve import serve_static

async def http(scope, receive, send):
    url = scope['raw_path'].decode('utf-8')

    match url:
        case '/users':
            pass
        case '/articles':
            pass
        case '/assets':
            await serve_static(send, './site/main.html')
        case _:
            await send(rstart404)
            await send(rbody(f"Error 404: URL {url} not found".encode('utf-8')))



