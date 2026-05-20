from dataclasses import dataclass, field
from typing import TypeVar


ResultT = TypeVar("ResultT")
ErrorT = TypeVar("ErrorT")


@dataclass(frozen=True)
class Response:
    pass


@dataclass(frozen=True)
class OkResponse[ResultT](Response):
    status: int = 200
    result: ResultT | None = None


@dataclass(frozen=True)
class ErrorData[ErrorT]:
    title: str = "Unknown error occurred"
    data: ErrorT | None = None


@dataclass(frozen=True)
class ErrorResponse[ErrorT](Response):
    status: int = 500
    error: ErrorData[ErrorT] = field(default_factory=ErrorData)
