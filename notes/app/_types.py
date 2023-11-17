from typing import Callable, Awaitable
from uvicorn._types import HTTPScope

# uvicorn scope, recieve, send types
uvc_scope = HTTPScope
uvc_recieve = Callable[[], Awaitable]
uvc_send = Callable[[dict], Awaitable]

asgi_app = Callable[[uvc_scope, uvc_recieve, uvc_send], Awaitable]
