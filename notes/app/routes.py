import pdb
import json
from codecs import getencoder
from config import assetsdir
from app.app import App
from app.responses import rbody, rstart200_json, rstart201_html


async def read_body(receive) -> str:
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body.decode('utf-8')


@App.route(
    r"^/profiles/(.+)/?.*$",
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
            response_body = await p.queryfilter('uname', resource_path, **querystring_args) or None
            await send(rstart200_json)
            await send(rbody(json.dumps(response_body).encode('utf_8')))
    else:
        raise ValueError("invalid querystring")


@App.route(
    r"^/assets/upload/?.*$",
    scope_params={"method": "POST"},
    qs_args={"owner": "string", "title": "string", "parentid": "string"}
)
async def post_asset(scope, recieve, send):
    querystring_args = scope["qs_args"]

    owner = querystring_args.get("owner")
    title = querystring_args.get("title")
    parentid = querystring_args.get("parentid")

    assets = scope['state']['assets']
    body = await read_body(recieve)
    async with assets() as a:
        if owner and parentid:
            new_row = await a.insert(["owner", "parentid"], [owner, parentid], returning=True, encoding=None)
            parentid = new_row["parentid"]
        elif owner and title:
            new_row = await a.insert(["owner", "title"], [owner, title], returning=True, encoding=None)
            parentid = new_row["parentid"]
        else:
            raise ValueError("invalid querystring")
    asset = assetsdir / str(parentid)
    with open(asset, mode="x") as newasset:
        newasset.write(body)

    await send(rstart201_html)
    await send(rbody(None))
