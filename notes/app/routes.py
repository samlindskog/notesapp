import logging
import re

from app.app import App
from app.responses import rbody, rstart200_json
from repository.objects import ProfilesRepository

#loop through and return full body of request
async def read_body(receive):
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body

@App.route(r"/profiles/.+")
async def run_profiles(scope, recieve, send):
    #less clunky then passing previous match through parameters
    pattern = re.compile(pattern=r"/.+/(.+)")
    pattern_match = pattern.search(scope["path"])
    assert isinstance(pattern_match, re.Match)

    resource_path = pattern_match.group(1)
    request_body = await read_body(recieve)

    profiles = scope['state']['profiles']
    
    if resource_path:
        async with profiles() as p:
            response_body = await p.queryfilter('uname', resource_path) or None
            await send(rstart200_json)
            await send(rbody(response_body))

