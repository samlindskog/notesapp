def r(body, more=False):
    return {
        'type': 'http.response.body',
        'body': body,
        'more_body': more
    }
