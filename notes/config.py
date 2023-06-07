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


