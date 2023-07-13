import os.path

async def test_site(send):
    filepath = os.path.abspath("./site/main.html")
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
