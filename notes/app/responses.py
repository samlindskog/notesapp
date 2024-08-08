rstart404_html = {
    "type": "http.response.start",
    "status": 404,
    "headers": [
        [b"content-type", b"text/plain; charset=utf-8"],
    ],
}

rstart404_json = {
    "type": "http.response.start",
    "status": 404,
    "headers": [
        [b"content-type", b"application/ld+json"],
    ],
}

rstart400_json = {
    "type": "http.response.start",
    "status": 400,
    "headers": [
        [b"content-type", b"application/ld+json"],
    ],
}

rstart400_html = {
    "type": "http.response.start",
    "status": 400,
    "headers": [
        [b"content-type", b"text/plain; charset=utf-8"],
    ],
}
rstart200_json = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"application/ld+json"],
        [b"Access-Control-Allow-Origin", b"*"],
        [b"Access-Control-Allow-Method", b"GET"],
        [b"Access-Control-Allow-Headers", b"*"],
        [b"Access-Control-Expose-Headers", b"*"],
    ]
}

rstart200_html = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"text/plain; charset=utf-8"],
    ],
}

rstart200_jpeg = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"image/jpeg"],
        [b"Access-Control-Allow-Origin", b"*"],
        [b"Access-Control-Allow-Method", b"GET"],
        [b"Access-Control-Allow-Headers", b"*"],
        [b"Access-Control-Expose-Headers", b"*"],
    ]
}

rstart200_pdf = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"application/pdf"],
        [b"Access-Control-Allow-Origin", b"*"],
        [b"Access-Control-Allow-Method", b"GET"],
        [b"Access-Control-Allow-Headers", b"*"],
        [b"Access-Control-Expose-Headers", b"*"],
    ]
}

rstart201_html = {
    "type": "http.response.start",
    "status": 201,
    "headers": [
        [b"content-type", b"text/plain; charset=utf-8"],
    ],
}

def rbody(
    body: bytes | None, more: bool = False
) -> dict[str, str | bytes | bool | None]:
    return {"type": "http.response.body", "body": body, "more_body": more}
