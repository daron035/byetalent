import logging

import uvicorn

from fastapi import FastAPI

from src.presentation.api.config import APIConfig
from src.presentation.api.controllers.main import setup_controllers
from src.presentation.api.controllers.responses.orjson import ORJSONResponse
from src.presentation.api.middlewares.main import setup_middlewares


logger = logging.getLogger(__name__)


def init_api(
    debug: bool = __debug__,
) -> FastAPI:
    logger.debug("Initialize API")
    app = FastAPI(
        debug=debug,
        title="Camirix Integrations",
        version="1.0.0",
        default_response_class=ORJSONResponse,
    )
    setup_middlewares(app)
    setup_controllers(app)
    return app


async def run_api(app: FastAPI, cfg: APIConfig) -> None:
    config = uvicorn.Config(
        app,
        host=cfg.host,
        port=cfg.port,
        log_level=logging.INFO,
        log_config=None,
        reload=True,
    )
    server = uvicorn.Server(config)
    logger.info("Running API")
    await server.serve()
