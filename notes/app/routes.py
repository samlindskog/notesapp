import pdb
import json
import logging
from pathlib import Path
from os.path import abspath

from app._types import uvc_recieve
from config import assetsdir
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget
from app.app import App
from app.responses import rbody, rstart200_json, rstart201_html


class MaxSizeValidator:
    _chunksize = 0

    def __init__(self, max_size: int, filepath: Path):
        self._filepath = filepath
        self._max_size = max_size

    def callback(self, chunk: bytes) -> None:
        self._chunksize += len(chunk)
        if self._chunksize > self._max_size:
            logging.debug("rolling back new file on disk")
            self._filepath.unlink(missing_ok=True)
            raise ValueError("maximum file size exceeded")


async def parse_file_to_disk(
    recieve: uvc_recieve,
    headers: dict[str, str],
    filepath: Path,
    max_size: int = 100000,
) -> None:
    parser = StreamingFormDataParser(headers=headers)
    callback = MaxSizeValidator(max_size, filepath).callback
    str_filepath = abspath(filepath)
    file_target = FileTarget(str_filepath, allow_overwrite=False, validator=callback)
    parser.register("file", file_target)

    more_body = True
    while more_body:
        data = await recieve()
        parser.data_received(data.get("body", b""))
        more_body = data.get("more_body", False)


async def read_body(receive: uvc_recieve) -> str:
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)
    return body.decode("utf-8")


@App.route(
    r"^/profiles/(.+)/?.*$",
    scope_params={"method": "GET"},
    qs_args={"orderby": "string", "limit": "int", "offset": "int", "desc": "bool"},
)
async def get_profiles(scope, recieve, send):
    profiles = scope["state"]["profiles"]
    resource_path = scope["group"][0]
    querystring_args = scope["qs_args"]

    if resource_path:
        async with profiles() as p:
            response_body = (
                await p.queryfilter("uname", resource_path, **querystring_args) or None
            )
            await send(rstart200_json)
            await send(rbody(json.dumps(response_body).encode("utf_8")))
    else:
        raise ValueError("invalid querystring: mandatory parameters missing")


@App.route(
    r"^/assets/upload/?.*$",
    scope_params={"method": "POST"},
    qs_args={"uname": "string", "title": "string", "parentpk": "string"},
)
async def post_asset(scope, recieve, send):
    assets = scope["state"]["assets"]
    querystring_args = scope["qs_args"]

    uname = querystring_args.get("uname", "")
    parentid = querystring_args.get("parentpk", "")
    title = querystring_args.get("title", "")

    async with assets() as a:
        if uname and parentid:
            new_row = await a.insert(
                ["uname", "parentpk"], [uname, parentid], returning=True, encoding=None
            )
            pk = new_row["pk"]
        elif uname and title:
            new_row = await a.insert(
                ["uname", "title"], [uname, title], returning=True, encoding=None
            )
            pk = new_row["pk"]
        else:
            raise ValueError("invalid querystring: mandatory parameters missing")
        filepath = assetsdir / (str(pk) + ".tex")
        headers = {a.decode("utf-8"): b.decode("utf-8") for a, b in scope["headers"]}
        await parse_file_to_disk(recieve, headers, filepath, max_size=10000000)

    await send(rstart201_html)
    await send(rbody(None))


@App.route(
    r"^/assets/upload/?.*$", scope_params={"method": "DELETE"}, qs_args={"pk": "string"}
)
async def delete_asset(scope, recieve, send):
    assets = scope["state"]["assets"]
    querystring_args = scope["qs_args"]

    pk = querystring_args.get("pk", "")
    async with assets() as a:
        if pk:
            await a.delete("pk", pk)
        else:
            raise ValueError("invalid querystring: mandatory parameters missing")
        filepath = assetsdir / (str(pk) + ".tex")
        logging.debug("deleting" + abspath(filepath))
        filepath.unlink(missing_ok=True)
