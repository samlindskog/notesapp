import uvicorn

def config_factory(config):
    match config:
        case 'development':
            return uvicorn.Config(
                app="main:app",
                reload=True,
            )
    return uvicorn.Config(
        app="main:app",
    )

_conninfo = ""
_connectargs = {}

async_pool_config = {
    "conninfo": _conninfo,
    "min_size": 2,
    "max_size": 20,
    "kwargs": _connectargs, #args for connect()
    "open": False,
    "max_idle": 1, #idle time of connection before it is closed
    "num_workers": 3 #number of threads used by connectionpool
}
