rstart404 = {
    'type': 'http.response.start',
    'status': 404,
    'headers': [
        [b'content-type', b'text/html'],
    ]
}

rstart200_json = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [
        [b'content-type', b'application/ld+json'],
    ]
}

rstart200_html = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [
        [b'content-type', b'text/html'],
    ]
}

def rbody(body, more=False):
    return {
        'type': 'http.response.body',
        'body': body,
        'more_body': more
}
