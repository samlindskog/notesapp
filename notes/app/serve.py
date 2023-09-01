import os.path

async def serve_static(send, path):
    filepath = os.path.abspath(path)
    file = open(filepath, mode='r')
    response = file.read().encode('utf-8')
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [b'content-type', b'text/html'],
        ]
    })
    await send({
        'type': 'http.response.body',
        'body': response,
    })
    file.close()
