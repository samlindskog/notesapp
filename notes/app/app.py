import logging
import re
import pdb
from typing import Callable
from app._types import uvc_scope, uvc_recieve, uvc_send, asgi_app
from urllib.parse import parse_qs
from app.responses import rstart404_html, rstart400_html, rbody

"""
Routing within App is determined by a decorator @App.route(path, scope_params={str:str, qs_args={str:str})
on the desired callback. If the request matches the pattern(s) specified, the callback
is ran. The "path" argument is a regex pattern used to match against scope["path"].
the optional "scope_params" argument is a dictionary with entries of the form
{key: value} with scope["key"]="value", matched verbatim against the request scope. qs_args
matches a request query string against expected args, and checks if their type is compatible.
https://asgi.readthedocs.io/en/latest/specs/www.html for more details.
"""


class App:
    # [scope_key, ...]
    _route_scope_keys = []
    # [[path, [scope_value, ...], callback], ...]
    _routes = []

    def _inject_scope(self, scope: uvc_scope, params: dict) -> None:
        for key in params.keys():
            scope[key] = params[key]

    async def run(self, scope: uvc_scope, recieve: uvc_recieve, send: uvc_send) -> None:
        try:
            current_path = scope["path"]
            current_scope_values = [scope[k] for k in self._route_scope_keys]
            # sorted for match against route_scope_values
            current_scope_values.sort()
            for route in self._routes:
                if not current_path:
                    break
                pattern = re.compile(route[0])
                match = pattern.fullmatch(current_path)
                if not match:
                    continue
                if not current_scope_values:
                    self._inject_scope(
                        scope,
                        {
                            "group": list(match.groups()),
                            "qs_args": self._querystring_argparser(
                                scope["query_string"], route[2]
                            ),
                        },
                    )
                    # run callback with current request parameters
                    await route[3](scope, recieve, send)
                    break
                route_scope_values = [v for k, v in route[1].items()]
                # sorted for match against current_scope_values
                route_scope_values.sort()
                for route_value, current_value in zip(
                    route_scope_values, current_scope_values
                ):
                    if route_value == current_value:
                        continue
                    # don't match empty route parameters
                    elif route_value == "":
                        continue
                    else:
                        break
                else:
                    self._inject_scope(
                        scope,
                        {
                            "group": list(match.groups()),
                            "qs_args": self._querystring_argparser(
                                scope["query_string"], route[2]
                            ),
                        },
                    )
                    # run callback with current request parameters
                    await route[3](scope, recieve, send)
                    break
            else:
                # if no matches found, return error 404
                await send(rstart404_html)
                await send(
                    rbody(f"Error 404: URL {current_path} not found".encode("utf-8"))
                )
        except ValueError as e:
            logging.debug(str(e))
            await send(rstart400_html)
            await send(rbody("Error 400: bad request :(".encode("utf-8")))

    # parse querystring to dictionary and decode b"key":[b"value"] pairs
    # maybe this shouldn't be a seperate function
    def _querystring_decode(self, query_string: bytes) -> dict[str, str]:
        query_dictionary = parse_qs(query_string, strict_parsing=True, errors="strict")
        return {
            k.decode("utf-8"): v[0].decode("utf-8") for k, v in query_dictionary.items()
        }

    """
    query_string is a percent encoded querystring, and target_args is a dictionary comprised
    of argument keywords with their respective type, i.e. {arg: type}. return a list of 
    parameters present in querystring which match target_args.

    will ignore empty or extraneous query params

    throws exceptions when params matching target_args are invalid, or if querystring itself
    is invalid
    """
    # this deserves a second glance, pretty sure it is poopoo

    def _querystring_argparser(
        self, query_string: bytes, target_args: dict[str, str]
    ) -> dict[str, str]:
        query_dictionary = self._querystring_decode(query_string)
        args = [
            [k, v, target_args[k]]
            for k, v in query_dictionary.items()
            if k in target_args.keys()
        ]
        valid_args = {}
        for arg in args:
            key = arg[0]
            value = arg[1]
            t = arg[2]
            if not value:
                raise ValueError("invalid querystring: empty parameter")
            match t:
                case "string":
                    valid_args[key] = value
                case "int":
                    if len(value) > 2:
                        raise ValueError(
                            "invalid querystring: value of type int exceeds length 2"
                        )
                    valid_args[key] = int(value)
                case "bool":
                    if value == "true":
                        valid_args[key] = True
                    elif value == "false":
                        valid_args[key] = False
                    else:
                        raise ValueError(
                            "invalid querystring: value could not be converted to type bool"
                        )
                case _:
                    raise ValueError("invalid target_args: type unsupported")
        if not valid_args:
            raise ValueError("invalid querystring: no valid parameters")
        return valid_args

    """
    route is a decorator, registering decorated function with a route, calling
    it when an incoming request matches specified conditions, sending 400 errors
    if request queryparameters are invalid.

    path is regex pattern matched against scope["path"]. All groups are
    matched and passed as a list into scope["group"] for decorated function.

    scope_params must contain the same keys for each invocation of App.route().

    qs_args, of the form {"key":"type", ...} specifies valid query string for given request path,
    and what to parse into dictionary which is passed into scope["qs_args"] for decorated
    function.
    """

    @classmethod
    def route(
        cls,
        path: str,
        scope_params: dict[str, str] | None = None,
        qs_args: dict[str, str] = {},
    ) -> Callable[[asgi_app], asgi_app]:
        def wrapper(fn):
            # scope params that are safely mutable
            mscope_params = scope_params or {}
            scope_items = mscope_params.items()
            scope_keys = [k for k, v in mscope_params.items()]
            scope_keys.sort()
            if not cls._routes:
                cls._route_scope_keys = scope_keys
            elif cls._routes[-1] and scope_keys != cls._route_scope_keys:
                raise ValueError("App.route param keys differ")
            # list of routes
            cls._routes.append([path, scope_params, qs_args, fn])
            return fn

        return wrapper
