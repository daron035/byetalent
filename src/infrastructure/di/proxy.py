from contextlib import asynccontextmanager
from typing import Any

from dishka import AsyncContainer, Scope
from memediator import Mediator

from src.application.common.core.interfaces import UseCase


class DiContainer:
    def __init__(self, root_container: AsyncContainer = None):  # type: ignore
        # Используем __dict__, чтобы проверка не уходила в рекурсию через __getattr__
        if "_root_container" not in self.__dict__:
            self._root_container = root_container

    def set_root(self, root_container: AsyncContainer) -> None:
        self._root_container = root_container

    @property
    def root(self) -> AsyncContainer:
        if self._root_container is None:
            raise RuntimeError("DI Container is not initialized! Call set_root() first.")
        return self._root_container

    def __call__(self, scope: Scope = Scope.REQUEST):
        return self.root(scope=scope)

    @asynccontextmanager
    async def request_scope(self):
        """Bind the request-scoped container to the mediator."""
        async with self.root() as request_container:
            mediator = await request_container.get(Mediator)
            mediator._ioc._root_container = request_container
            yield request_container


class UseCaseProxy(DiContainer):
    async def execute(self, use_case: type[UseCase], *args: Any, **kwargs: Any) -> Any:
        async with self.request_scope() as request_container:
            usecase_instance = await request_container.get(use_case)
            return await usecase_instance.execute(*args, **kwargs)


class MediatorProxy(DiContainer):
    def __getattr__(self, name: str) -> Any:
        async def _wrapped(*args: Any, **kwargs: Any) -> Any:
            mediator = await self.root.get(Mediator)
            method = getattr(mediator, name)
            return await method(*args, **kwargs)

        return _wrapped


container = DiContainer()
use_case = UseCaseProxy()
mediator = MediatorProxy()


def setup_proxy_di(app_container: AsyncContainer) -> None:
    container.set_root(app_container)
    use_case.set_root(app_container)
    mediator.set_root(app_container)
