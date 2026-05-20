from dishka import Provider, Scope
from memediator import EventMediator, Mediator

from src.infrastructure.config import Config
from src.infrastructure.di.mediator import build_mediator
from src.infrastructure.log.config import LoggingConfig
from src.infrastructure.log.event_handler import EventLogger
from src.infrastructure.persistence.postgres.config import PostgresConfig
from src.infrastructure.persistence.postgres.main import (
    build_sa_engine,
    build_sa_session,
    build_sa_session_factory,
)
from src.infrastructure.persistence.postgres.services.healthcheck import PgHealthCheck, PostgresHealthcheckService
from src.infrastructure.persistence.postgres.uow import SQLAlchemyUoW
from src.infrastructure.uow import build_uow


def config_provider(config: Config) -> Provider:
    provider = Provider()

    # Config
    provider.provide(lambda: config.db, scope=Scope.APP, provides=PostgresConfig)
    provider.provide(lambda: config.logging, scope=Scope.APP, provides=LoggingConfig)

    # Mediator
    provider.provide(build_mediator, scope=Scope.APP, provides=Mediator)
    provider.alias(source=Mediator, provides=EventMediator)
    provider.provide(EventLogger, scope=Scope.REQUEST)

    # Postgres
    provider.provide(build_sa_engine, scope=Scope.APP)
    provider.provide(build_sa_session_factory, scope=Scope.APP)
    provider.provide(build_sa_session, scope=Scope.REQUEST)

    # UoW
    provider.provide(SQLAlchemyUoW, scope=Scope.REQUEST)
    provider.provide(build_uow, scope=Scope.REQUEST)

    # Repositories
    provider.provide(PostgresHealthcheckService, scope=Scope.REQUEST, provides=PgHealthCheck)

    return provider
