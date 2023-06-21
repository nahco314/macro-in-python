import ast
import inspect
from abc import ABC, abstractmethod
from copy import copy, deepcopy
from textwrap import dedent
from types import FunctionType
from typing import Any, Callable, Generic, Optional, ParamSpec, TypeVar

import macro_in_python.errors as errors
from macro_in_python.utils import get_source

T = TypeVar("T")
P = ParamSpec("P")


class Macro(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def apply(self, original: ast.AST, args: P.args, kwargs: P.kwargs) -> Any:
        raise NotImplementedError


class FuncMacro(Macro, ABC, Generic[P, T]):
    def __init__(
        self, name: str, func: Callable[P, T], *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(name)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        raise errors.MacroSyntaxError(f"Macro.__call__ cannot be called.")


class SyntaxMacro(FuncMacro):
    def __init__(
        self, name: str, func: Callable[P, T], body_ast: list[ast.stmt]
    ) -> None:
        super().__init__(name, func)
        self.func = func
        self.body_ast = body_ast

    def apply(
        self, original: ast.AST, args: P.args, kwargs: P.kwargs
    ) -> list[ast.stmt]:
        call_args = inspect.getcallargs(self.func, *args, **kwargs)
        result = [NameReplacer(call_args).visit(node) for node in self.body_ast]
        return result


class ExprMacro(FuncMacro):
    def __init__(self, name: str, func: Callable[P, T], expr_ast: ast.expr) -> None:
        super().__init__(name, func)
        self.func = func
        self.expr_ast = expr_ast

    def apply(self, original: ast.AST, args: P.args, kwargs: P.kwargs) -> ast.expr:
        expr_ast = deepcopy(self.expr_ast)
        call_args = inspect.getcallargs(self.func, *args, **kwargs)
        result = NameReplacer(call_args).visit(expr_ast)
        return result


class NameReplacer(ast.NodeTransformer):
    def __init__(self, name_map: dict[str, ast.expr]) -> None:
        self.name_map = name_map

    def visit_Name(self, node: ast.Name) -> ast.expr:
        if node.id in self.name_map:
            res = copy(self.name_map[node.id])

            if isinstance(getattr(res, "ctx", None), ast.Load):
                if not hasattr(res, "ctx"):
                    raise errors.MacroSyntaxError(
                        "Expression that cannot be changed is changed."
                    )

                res.ctx = node.ctx

            return res
        else:
            return node


def macro(
    func: Callable[P, T], tree: Optional[ast.FunctionDef] = None
) -> FuncMacro[P, T]:
    if tree is None:
        assert isinstance(func, FunctionType)
        func_tree = ast.parse(dedent(get_source(func)))
        assert len(func_tree.body) == 1
        tree = func_tree.body[0]
        assert isinstance(tree, ast.FunctionDef)

    assert len(tree.body) > 0

    if len(tree.body) == 1:
        s = tree.body[0]
        if isinstance(s, ast.Expr):
            expr = s.value

            return ExprMacro(func.__name__, func, expr)

    return SyntaxMacro(func.__name__, func, tree.body)
