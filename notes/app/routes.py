import pdb
import json
from app.app import App
from app.responses import rbody, rstart200_json


async def read_body(receive) -> str:
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body.decode('utf-8')


@App.route(
    r"^/profiles/(.+)/?$",
    scope_params={"method": "GET"},
    qs_args={"orderby": "string", "limit": "int",
             "offset": "int", "desc": "bool"}
)
async def get_profiles(scope, recieve, send) -> None:
    resource_path = scope["group"][0]
    querystring_args = scope["qs_args"]
    profiles = scope['state']['profiles']
    body = await read_body(recieve)

    if resource_path:
        async with profiles() as p:
            response_body = await p.queryfilter('uname', resource_path, **querystring_args, encode='utf-8') or None
            await send(rstart200_json)
            await send(rbody(json.dumps(response_body).encode('utf_8')))
    else:
        raise Exception("send did not run")


@App.route(
    r"^/assets/upload/?$",
    scope_params={"method": "POST", "content-type": "multipart/form-data"},
    qs_args={"owner": "string", "title": "string", "parentid": "string"}
)
async def post_asset(scope, recieve, send):
    querystring_args = scope["qs_args"]

    owner = querystring_args.get("owner")
    title = querystring_args.get("title")
    parentid = querystring_args.get("parentid")

    assets = scope['state']['assets']
    body = await read_body(recieve)
    querystring_args = json.loads(body)

    async with assets() as a:
        if owner and title:
            _ = await a.insert(["owner", "title"], None, **querystring_args) or None
        if owner and parentid:
            _ = await a.insert(["owner", "parentid"], None, **querystring_args) or None
        await send(rstart200_json)
        await send(rbody())
