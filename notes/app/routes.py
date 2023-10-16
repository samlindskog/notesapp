import pdb

from app.app import App
from app.responses import rbody, rstart200_json

async def read_body(receive):
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body

@App.route(
        r"/profiles/(.+)/",
        scope_params={"method": "GET"},
        qs_args={"orderby": "string","limit": "int","offset": "int","desc": "bool"})
async def run_profiles(scope, recieve, send):
    resource_path = scope["group"][0]
    querystring_args = scope["qs_args"]
    profiles = scope['state']['profiles']
    body = await read_body(recieve)
    
    if resource_path:
        async with profiles() as p:
            response_body = await p.queryfilter('uname', resource_path, **querystring_args) or None
            await send(rstart200_json)
            await send(rbody(response_body))
    else:
        raise Exception("send did not run")

