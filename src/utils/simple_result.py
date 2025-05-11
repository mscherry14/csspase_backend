from dataclasses import dataclass
from typing import TypeAlias, Union, TypeVar

T = TypeVar('T')

@dataclass
class SimpleOkResult[T]:
    payload: T

@dataclass
class SimpleErrorResult[T]:
    message: str

SimpleResult: TypeAlias = Union[
    SimpleErrorResult[T],
    SimpleOkResult[T]
]