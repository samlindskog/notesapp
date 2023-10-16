import logging
import re
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
    _scope_params = []
    #[[path, [scope_value, ...], callback], ...]
    _routes = []

    async def run(self, scope, recieve, send):
        current_scope_values = self._scope_values(scope) or []
        try:
            for route in self._routes:
                pattern = re.compile(route[0])
                match = pattern.match(scope["path"])
                if not match:
                    continue
                elif not current_scope_values:
                    #run callback with current request parameters
                    await route[2](scope, recieve, send)
                    break
                for param in current_scope_values:
                    if route[1] == param:
                        await route[2](scope, recieve, send)
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

  
    #params must contain the same keys for each invocation
    @classmethod
    def route(cls, path, params={}):
        def wrapper(fn):
            param_items = params.items()
            param_values = [v for k,v in param_items].sort()
            #list of scope keys
            cls._scope_params = [k for k,v in param_items]
            #sorted list of scope values from params dictionary
            cls._routes.append([path, param_values, fn])
            return fn
        return wrapper

    def _scope_values(self, scope):
        current_request_params = [scope[key] for key in self._scope_params]
        #sorted list of scope values with keys from self._scope_params dictionary
        return current_request_params.sort()

