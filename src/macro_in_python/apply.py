import ast
from types import FunctionType
from typing import Callable, Optional, TypeVar, cast

import macro_in_python.errors as errors
from macro_in_python.macro import ExprMacro, Macro, SyntaxMacro
from macro_in_python.utils import get_source

F = TypeVar("F", bound=FunctionType)


class MacroApplier(ast.NodeTransformer):
    def __init__(self, macro_map: dict[str, Macro]) -> None:
        self.macro_map = macro_map

    def visit_Expr(self, node: ast.Expr) -> list[ast.stmt]:
        value = node.value

        if not isinstance(value, ast.Call):
            return [cast(ast.Expr, self.generic_visit(node))]

        func = value.func
        if not isinstance(func, ast.Name):
            return [cast(ast.Expr, self.generic_visit(node))]
        if func.id not in self.macro_map:
            return [cast(ast.Expr, self.generic_visit(node))]

        macro_ = self.macro_map[func.id]
        if not isinstance(macro_, SyntaxMacro):
            return [cast(ast.Expr, self.generic_visit(node))]

        if any(isinstance(arg, ast.Starred) for arg in value.args):
            raise errors.MacroSyntaxError(
                "Starred argument is not allowed in syntax macro."
            )
        if any(isinstance(kw.value, ast.Starred) for kw in value.keywords):
            raise errors.MacroSyntaxError(
                "Starred argument is not allowed in syntax macro."
            )

        args = [self.visit(cast(ast.expr, arg)) for arg in value.args]
        kwargs = {kw.arg: self.visit(cast(ast.expr, kw.value)) for kw in value.keywords}

        try:
            result = macro_.apply(node, args, kwargs)
        except TypeError as e:
            raise errors.MacroSyntaxError(f"Call to {macro_.name} failed: {e}") from e

        return result

    def visit_Call(self, node: ast.Call) -> ast.expr:
        func = node.func
        if not isinstance(func, ast.Name):
            return cast(ast.expr, self.generic_visit(node))
        if func.id not in self.macro_map:
            return cast(ast.expr, self.generic_visit(node))

        macro_ = self.macro_map[func.id]
        if not isinstance(macro_, ExprMacro):
            if isinstance(macro_, SyntaxMacro):
                raise errors.MacroSyntaxError("Syntax macro cannot be used as expr.")
            else:
                assert False

        if any(isinstance(arg, ast.Starred) for arg in node.args):
            raise errors.MacroSyntaxError(
                "Starred argument is not allowed in syntax macro."
            )
        if any(isinstance(kw.value, ast.Starred) for kw in node.keywords):
            raise errors.MacroSyntaxError(
                "Starred argument is not allowed in syntax macro."
            )

        args = [self.visit(cast(ast.expr, arg)) for arg in node.args]
        kwargs = {kw.arg: self.visit(cast(ast.expr, kw.value)) for kw in node.keywords}

        return macro_.apply(node, args, kwargs)


def apply_ast(func: F, *macros, tree: Optional[ast.FunctionDef] = None) -> ast.Module:
    applier = MacroApplier({macro_.name: macro_ for macro_ in macros})

    if tree is None:
        source = get_source(func)
        _first = ast.parse(source).body[0]
        assert isinstance(_first, ast.FunctionDef)
        tree = _first

    applied_body = applier.visit(tree).body

    applied_ast = ast.Module(applied_body, [])
    ast.fix_missing_locations(applied_ast)

    return applied_ast


def apply(*macros: Macro) -> Callable[[F], F]:
    def inner(func: F) -> F:
        code = compile(apply_ast(func, *macros), filename="<macro>", mode="exec")  # type: ignore

        new_func = FunctionType(
            code,
            func.__globals__,
            func.__name__,
            func.__defaults__,
            (),
        )

        new_func.__code__ = code

        return cast(F, new_func)

    return inner
