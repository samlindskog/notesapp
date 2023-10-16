import string
from typing import ByteString
from urllib.parse import parse_qs
import re
import pdb
import logging

from app.app import App
from app.responses import rbody, rstart200_json

#loop through and return full body of request
async def read_body(receive):
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body

#parse querystring to dictionary and decode b"key":[b"value"] pairs
def _querystring_decode(query_string):
    query_dictionary = parse_qs(query_string, strict_parsing=True, errors="strict")
    return {k.decode("utf-8"): v[0].decode("utf-8") for k, v in query_dictionary.items()}

'''
query_string is a percent encoded querystring, and target_args is a dictionary comprised
of argument keywords with their respective type, i.e. {arg: type}. return a list of 
parameters present in querystring which match target_args.

will ignore empty or extraneous query params

throws exceptions when params matching target_args are invalid, or if querystring itself
is invalid
'''
def _querystring_argparser(query_string, target_args):
    query_dictionary = _querystring_decode(query_string)
    args = [[k,v, target_args[k]] for k,v in query_dictionary.items() if k in target_args.keys()]
    valid_args = {}
    for arg in args:
        key = arg[0]
        value = arg[1]
        t=arg[2]
        if not value:
            raise Exception("invalid querystring: empty parameter")
        match t:
            case "string":
                valid_args[key] = value
            case "int":
                if len(value) > 2:
                    raise Exception("invalid querystring: value of type int exceeds length 2")
                valid_args[key] = int(value)
            case "bool":
                if value == "true":
                    valid_args[key] = True
                elif value == "false":
                    valid_args[key] = False
                else:
                    raise Exception("invalid querystring: value of type bool invalid")
            case _:
                raise Exception("invalid target_args: type unsupported")
    return valid_args

@App.route(r"/profiles/.+/")
async def run_profiles(scope, recieve, send):
    #less clunky then passing previous match through parameters
    pattern = re.compile(pattern=r"/profiles/(.+)/")
    pattern_match = pattern.search(scope["path"])
    assert isinstance(pattern_match, re.Match), "pattern match null"
    
    request_body = await read_body(recieve)
    resource_path = pattern_match.group(1)
    querystring_args = _querystring_argparser(
            scope["query_string"], {"orderby": "string","limit": "int","offset": "int","desc": "bool"})



    profiles = scope['state']['profiles']
    
    if resource_path:
        async with profiles() as p:
            response_body = await p.queryfilter('uname', resource_path, **querystring_args) or None
            await send(rstart200_json)
            await send(rbody(response_body))
    else:
        print("value error")
        raise Exception("send did not run")

