from abc import abstractmethod
from typing import Protocol

import sqlalchemy as sa

from src.infrastructure.persistence.postgres.repositories.base import SQLAlchemyRepo


class PgHealthCheck(Protocol):
    @abstractmethod
    async def check(self) -> dict[str, bool]:
        raise NotImplementedError


class PostgresHealthcheckService(SQLAlchemyRepo, PgHealthCheck):
    async def check(self) -> dict[str, bool]:
        cursor = await self.session.execute(sa.select(1))
        result = cursor.scalar()
        return {self.__class__.__name__: result == 1}
