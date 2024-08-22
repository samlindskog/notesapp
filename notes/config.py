from pathlib import PosixPath
import uvicorn
from jinja2 import Environment, FileSystemLoader
from psycopg.rows import dict_row

from psycopg_pool import AsyncConnectionPool
from app.objects import Repository
from app.app import App

#global config
maindir = PosixPath(__file__).parent
assetsdir = maindir / "assets"
sitedir = maindir.parent / "site"
endpoint = "72.14.178.40"

def config_factory(config):
    match config:
        case "dev":
            return uvicorn.Config(
                app="main:app",
                reload=True,
            )
        case "prod":
            return uvicorn.Config(
                app="main:app",
                loop="uvloop",
                http="httptools"
            )
            pass
    return uvicorn.Config(
        app="main:app",
    )


_conninfo = "postgresql://notesapp@127.0.0.1:5432/notesapp"
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
    def template_env(self):
        return Environment(
                loader=FileSystemLoader(str(maindir / "templates")),
                autoescape=False,
                enable_async=True,
                )

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
