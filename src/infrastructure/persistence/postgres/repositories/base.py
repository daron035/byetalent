from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.postgres.exception_mapper import ExceptionMappingMeta


class SQLAlchemyRepo(metaclass=ExceptionMappingMeta):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
