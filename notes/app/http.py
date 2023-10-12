import logging
import re
import json
import time
import psycopg.errors
from psycopg_pool import AsyncConnectionPool
from app.responses import (rstart404, rstart200_json, rbody)
from repository.objects import AssetsRepository, ProfilesRepository

async def http(scope, receive, send):
    raw_path = scope['raw_path'].decode('utf-8')
    #pattern matching for url path
    profiles = re.compile(pattern=r"/profiles(.*)")
    assets = re.compile(pattern=r"/assets(.*)")
    #route requests
    if profiles.match(raw_path):
        await run_profiles(scope, receive, send)
    elif assets.match(raw_path):
        await run_assets(scope, receive, send)
    else:
        await send(rstart404)
        await send(rbody(f"Error 404: URL {raw_path} not found".encode('utf-8')))

#loop through and return full body of request
async def _read_body(receive):
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body

#profiles route
async def run_profiles(scope, recieve, send):
    pattern = re.compile(pattern=r"/.+/(.*)")
    pattern_match = pattern.search(scope["raw_path"].decode("utf-8"))
    assert isinstance(pattern_match, re.Match)

    query_string = pattern_match.group(1)
    #if query_string:
        #re.compile(r"")
        #match query_string:
            #case 

    request_body = await _read_body(recieve)


    profiles = scope['state']['profiles']
    profiles_repo = profiles()
    assert isinstance(profiles_repo, ProfilesRepository)

    async with profiles_repo as p:
        response_body = await p.queryfilter('uname', 'sam')

    print("rstart200_json")
    print(time.monotonic())
    await send(rstart200_json)
    print("response_body")
    print(time.monotonic())
    await send(rbody(response_body))
    print(time.monotonic)


#assets route
async def run_assets(scope, receive, send):
    pass
