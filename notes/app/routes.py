import pdb
import os
import json
import logging
from pathlib import Path
from os.path import abspath

import config
from app._types import uvc_recieve
from app.app import App
from app.responses import (
    rbody,
    rstart200_json,
    rstart200_jpeg,
    rstart200_pdf,
    rstart200_text,
    rstart400_html,
    rstart200_html,
)

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget
import jinja2

logger = logging.getLogger(__name__)

class MaxSizeValidator:
    _chunksize = 0

    def __init__(self, max_size: int, filepath: Path):
        self._filepath = filepath
        self._max_size = max_size

    def callback(self, chunk: bytes) -> None:
        self._chunksize += len(chunk)
        if self._chunksize > self._max_size:
            logger.debug("rolling back new file on disk")
            self._filepath.unlink(missing_ok=True)
            raise ValueError("maximum file size exceeded")


#not using this rn for anything, but it do work.
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

#not using this either
async def read_body(receive: uvc_recieve) -> str:
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)
    return body.decode("utf-8")

@App.route(
        r"^/assets/list$",
        scope_params={"method": "GET"}
        )
async def assetlist_get(scope, recieve, send):
    repository = scope["state"]["repository"]
    async with repository() as conn:
        async with conn.cursor() as acur:
            await acur.execute("SELECT * FROM notes.assets")
            recordset = await acur.fetchall()
            await send(rstart200_json)
            await send(rbody(json.dumps(recordset, default=str).encode("utf_8")))

@App.route(
        r"^/assets/view/([^\.]+)(\..+)$",
        scope_params={"method": "GET"}
        )
async def asset_viewer(scope, recieve, send):
    # for detecting file extension for correct mime type
    filename = scope["group"][0]
    extension = scope["group"][1]
    template_env = scope["state"]["template_env"]
    repository = scope["state"]["repository"]
    
    if not (filename and extension):
        raise ValueError("Bad filename")

    async with repository() as conn:
        async with conn.cursor() as acur:
            await acur.execute("SELECT * FROM notes.assets WHERE id=%s", [filename])
            recordset = await acur.fetchall()
            title = recordset[0]["title"]

    with open(config.assetsdir / (filename + extension), "rb") as f:
        file_bytes = f.read()
        match extension:
            case ".jpg":
                await send(rstart400_html)
                # prevent html_str possibly unbound error
                return
            case ".pdf":
                template = template_env.get_template("pdfviewer.html")
                html_str = await template.render_async(
                        title=title,
                        assetlink=f"//{config.endpoint}/assets/{filename}{extension}"
                    )
                await send(rstart200_html)
            case ".md":
                template = template_env.get_template("mdviewer.html")
                html_str = await template.render_async(
                        title=title,
                        assetlink=f"//{config.endpoint}/assets/{filename}{extension}"
                    )
                await send(rstart200_html)
            case _:
                html_str = "test"
        await send(rbody(html_str.encode()))

@App.route(
        r"^/assets/([^\.]+)(\..+)$",
        scope_params={"method": "GET"}
        )
async def asset_get(scope, recieve, send):
    # for detecting file extension for correct mime type
    filename = scope["group"][0]
    extension = scope["group"][1]
    
    if not (filename and extension):
        raise ValueError("Bad filename")

    if not os.path.exists(config.assetsdir / (filename + extension)):
        raise ValueError("Asset does not exist")

    with open(config.assetsdir / (filename + extension), "rb") as f:
        file_bytes = f.read()
        match extension:
            case ".jpg":
                await send(rstart200_jpeg)
            case ".pdf":
                await send(rstart200_pdf)
            case ".md":
                await send(rstart200_text)
        await send(rbody(file_bytes))

@App.route(
        r"^.*$",
        scope_params={"method": "OPTIONS"}
        )
async def cors_options(scope, recieve, send):
    def is_cors_header(h):
        cors_headers = [
                b"access-control-request-headers",
                b"access-control-request-method",
                ]
        for header in cors_headers:
            if h == header:
                return True

    headers = [i[0] for i in scope["headers"]]
    cors_headers = [i for i in headers if is_cors_header(i)]

    if not cors_headers:
        raise ValueError("No CORS headers present")

    rstart200_cors = {
        "type": "http.response.start",
        "status": 200,
        "headers": [
            [b"content-type", b"text/plain"],
            [b"Access-Control-Allow-Origin", b"*"],
            [b"Access-Control-Allow-Method", b"GET"],
            [b"Access-Control-Allow-Headers", b"*"],
            [b"Access-Control-Expose-Headers", b"*"],
        ]
    }
    
    await send(rstart200_cors)
    await send(rbody(b""))


'''
@App.route(
    r"^/profiles/(.+)/?.*$"
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
'''
