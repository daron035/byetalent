from typing import ParamSpec, Protocol, TypeVar, runtime_checkable


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


@runtime_checkable
class UseCase(Protocol[P, R_co]):
    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...
