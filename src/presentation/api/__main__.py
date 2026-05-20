import asyncio
import logging

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka import Scope, make_async_container

from src.infrastructure.config import Config
from src.infrastructure.config_loader import load_config
from src.infrastructure.di import config_provider
from src.infrastructure.di.proxy import setup_proxy_di
from src.infrastructure.log.main import configure_logging
from src.presentation.api.main import init_api, run_api


logger = logging.getLogger(__name__)


@asynccontextmanager
async def init_di(cfg: Config) -> AsyncGenerator[None]:
    runtime_container = make_async_container(config_provider(cfg), start_scope=Scope.RUNTIME)

    async with runtime_container(scope=Scope.APP) as app_container:
        setup_proxy_di(app_container)

        yield

        await app_container.close()


async def main() -> None:
    config, path = load_config(Config)
    configure_logging(config.logging)

    logger.info("Loaded config from %s", path)
    logger.info("Launch app", extra={"config": config})

    async with init_di(config):
        app = init_api()
        await run_api(app, config.api)


if __name__ == "__main__":
    asyncio.run(main())
