from dishka import Provider, Scope
from memediator import EventMediator, Mediator

from src.application.department.commands import (
    CreateDepartmentHandler,
    DeleteDepartmentHandler,
    UpdateDepartmentHandler,
)
from src.application.department.interfaces import DepartmentReader, DepartmentRepo
from src.application.department.queries import GetDepartmentByIdHandler
from src.application.department.use_cases import CreateDepartmentUseCase
from src.application.employee.commands import CreateEmployeeHandler
from src.application.employee.interfaces import EmployeeRepo
from src.application.employee.use_cases import CreateEmployeeUseCase
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
from src.infrastructure.persistence.postgres.repositories import DepartmentRepoImpl, EmployeeRepoImpl
from src.infrastructure.persistence.postgres.repositories.department import DepartmentReaderImpl
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

    # Use Cases
    provider.provide(CreateDepartmentUseCase, scope=Scope.REQUEST)
    provider.provide(CreateEmployeeUseCase, scope=Scope.REQUEST)

    # Command Handlers
    provider.provide(CreateDepartmentHandler, scope=Scope.REQUEST)
    provider.provide(DeleteDepartmentHandler, scope=Scope.REQUEST)
    provider.provide(UpdateDepartmentHandler, scope=Scope.REQUEST)
    provider.provide(CreateEmployeeHandler, scope=Scope.REQUEST)

    # Query Handlers
    provider.provide(GetDepartmentByIdHandler, scope=Scope.REQUEST)

    # Postgres
    provider.provide(build_sa_engine, scope=Scope.APP)
    provider.provide(build_sa_session_factory, scope=Scope.APP)
    provider.provide(build_sa_session, scope=Scope.REQUEST)

    # UoW
    provider.provide(SQLAlchemyUoW, scope=Scope.REQUEST)
    provider.provide(build_uow, scope=Scope.REQUEST)

    # Repositories
    provider.provide(DepartmentRepoImpl, scope=Scope.REQUEST, provides=DepartmentRepo)
    provider.provide(EmployeeRepoImpl, scope=Scope.REQUEST, provides=EmployeeRepo)

    provider.provide(DepartmentReaderImpl, scope=Scope.REQUEST, provides=DepartmentReader)

    # Repositories
    provider.provide(PostgresHealthcheckService, scope=Scope.REQUEST, provides=PgHealthCheck)

    return provider
