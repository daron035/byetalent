from collections.abc import Callable
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, ParamSpec, TypeVar, _ProtocolMeta, cast

from sqlalchemy.exc import SQLAlchemyError

from src.application.common.core.exceptions import RepoError


P = ParamSpec("P")
F = TypeVar("F", bound=Callable[..., Any])


def exception_mapper(func: F) -> F:
    @wraps(func)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as err:
            raise RepoError from err

    return cast("F", wrapped)


def no_exception_mapper(func: Any) -> Any:
    func.__no_exception_mapper__ = True
    return func


class ExceptionMappingMeta(_ProtocolMeta):
    def __new__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):
        for attr_name, attr_value in namespace.items():
            if (
                not attr_name.startswith("_")
                and iscoroutinefunction(attr_value)
                and not getattr(attr_value, "__no_exception_mapper__", False)
            ):
                namespace[attr_name] = exception_mapper(attr_value)

        return super().__new__(cls, name, bases, namespace)
