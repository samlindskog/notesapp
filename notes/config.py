from pathlib import PosixPath
import uvicorn
from psycopg.rows import dict_row

from psycopg_pool import AsyncConnectionPool
from app.objects import Repository
from app.app import App

maindir = PosixPath(__file__).parent
assetsdir = maindir / "assets"


def config_factory(config):
    match config:
        case "development":
            return uvicorn.Config(
                app="main:app",
                reload=True,
            )
    return uvicorn.Config(
        app="main:app",
    )


_conninfo = "postgresql://samuellindskog@127.0.0.1:5432/notesappdev"
_connectargs = {"row_factory": dict_row}

async_pool_config = {
    "conninfo": _conninfo,
    "min_size": 2,
    "max_size": 20,
    "kwargs": _connectargs,  # args for connect()
    "open": False,
    "max_idle": 1,  # idle time of connection before it is closed
    "num_workers": 3,  # number of threads used by connectionpool
}


class Resources:
    def __init__(self):
        self._aconnpool = AsyncConnectionPool(**async_pool_config)

    @property
    def current_pool(self):
        return self._aconnpool

    @property
    def repository(self):
        return Repository.use_async_connection_pool(self._aconnpool)

    @property
    def app(self):
        # Initialize routes
        import app.routes

        return App
