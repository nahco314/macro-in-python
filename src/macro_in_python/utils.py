import inspect
from collections.abc import Iterable
from textwrap import dedent
from types import FunctionType
from typing import Callable, TypeVar

T = TypeVar("T")


def get_source(func: FunctionType) -> str:
    return dedent(inspect.getsource(func))


def where(iter_: Iterable[T], pred: Callable[[T], bool]) -> int:
    for i, x in enumerate(iter_):
        if pred(x):
            return i
    raise ValueError("Not found")
