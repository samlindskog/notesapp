import uvicorn

import config as c

async def app(scope, receive, send):
    assert scope['type'] == 'http'
    event = await receive()
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [b'content-type', b'text/plain'],
        ]
    })
    await send({
        'type': 'http.response.body',
        'body': b'Hello, world!',
    })



if __name__ == "__main__":
    config = c.config_factory('development')
    server = uvicorn.Server(config)
    server.run()
