import logging
import re
import pdb
from urllib.parse import parse_qs
from app.responses import rstart404_html, rstart400_html, rbody

'''
Routing within App is determined by a decorator @App.route(path, params={key: value,})
on the desired callback. If the request matches the pattern(s) specified, the callback
is ran. The "path" argument is a regex pattern used to match against scope["path"], and 
the optional "params" argument is a dictionary with entries of the form
{key: value} with scope["key"]="value", matched verbatim against the request scope.
https://asgi.readthedocs.io/en/latest/specs/www.html for more details.
'''
class App():
    #[scope_key, ...]
    _route_scope_keys = []
    #[[path, [scope_value, ...], callback], ...]
    _routes = []

    def _inject_scope(self, scope, params):
        for key in params.keys():
            scope[key] = params[key]

    async def run(self, scope, recieve, send):
        try:
            current_scope_values = [scope[k] for k in self._route_scope_keys]
            current_scope_values.sort()
            for route in self._routes:
                pattern = re.compile(route[0])
                match = pattern.match(scope["path"])
                if not match:
                    continue
                elif not current_scope_values:
                    self._inject_scope(
                            scope, {
                            "group": list(match.groups()),
                            "qs_args": self._querystring_argparser(scope["query_string"], route[2])
                            })
                    #run callback with current request parameters
                    await route[3](scope, recieve, send)
                    break
                route_scope_values = [v for k,v in route[1].items()]
                route_scope_values.sort()
                if route_scope_values == current_scope_values:
                    self._inject_scope(
                            scope, {
                            "group": list(match.groups()),
                            "qs_args": self._querystring_argparser(scope["query_string"], route[2])
                            })
                    await route[3](scope, recieve, send)
                else:
                    continue
                break
            else:
                #if no matches found, return error 404
                await send(rstart404_html)
                await send(rbody(f"Error 404: URL {scope['path']} not found".encode('utf-8')))
        except Exception as e:
            logging.debug(str(e))
            await send(rstart400_html)
            await send(rbody("Error 400: bad request :(".encode('utf-8')))
    
    #parse querystring to dictionary and decode b"key":[b"value"] pairs
    def _querystring_decode(self, query_string):
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
    def _querystring_argparser(self, query_string, target_args):
        query_dictionary = self._querystring_decode(query_string)
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

    '''
    route is a decorator which runs decorated function when a request
    matches specified conditions

    path is regex pattern matched against scope["path"]. All groups are
    matched and passed as a list into scope["group"]

    params, of the form {"key": "value", ...}, is used to match requests
    whose scope["key"]=="value". Must contain the same keys for each
    invocation of App.route(). All filter params being specified by their
    keys in each invocation enhances readability, and mitigates phantom
    matches at runtime

    qs_args, of the form {"key":"type", ...} specifies how to
    parse query string parameters into a dictionary, with key matched
    against querystring keys, and type used to convert querystring
    values. The resulting dictionary is passed into scope["qs_args"]
    '''      
    @classmethod
    def route(cls, path, scope_params={}, qs_args={}):
        def wrapper(fn):
            scope_items = scope_params.items()
            scope_keys = [k for k,v in scope_params.items()]
            scope_keys.sort()
            if not cls._routes:
                cls._route_scope_keys = scope_keys
            #test this plz
            elif cls._routes[-1] and scope_keys != cls._route_scope_keys:
                raise Exception("App.route param keys differ")

            #list of routes
            cls._routes.append([path, scope_params, qs_args, fn])
            return fn
        return wrapper

