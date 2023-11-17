rstart404_html = {
    "type": "http.response.start",
    "status": 404,
    "headers": [
        [b"content-type", b"text/html"],
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
        [b"content-type", b"text/html"],
    ],
}
rstart200_json = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"application/ld+json"],
    ],
}

rstart200_html = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"text/html"],
    ],
}
rstart201_html = {
    "type": "http.response.start",
    "status": 201,
    "headers": [
        [b"content-type", b"text/html"],
    ],
}


def rbody(
    body: bytes | None, more: bool = False
) -> dict[str, str | bytes | bool | None]:
    return {"type": "http.response.body", "body": body, "more_body": more}
