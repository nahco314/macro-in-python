import ast
from copy import deepcopy
from pathlib import Path
from typing import Any

import macro_in_python.errors as errors
from macro_in_python.apply import apply_ast
from macro_in_python.macro import Macro, macro
from macro_in_python.utils import where


class FileConverter(ast.NodeTransformer):
    def __init__(self):
        self.macro_map: dict[str, Macro] = {}

    def visit_Import(self, node: ast.Import) -> ast.Import | None:
        new_names = []
        for alias in node.names:
            if alias.asname == "macro_in_python":
                continue
            new_names.append(alias)

        if len(new_names) == 0:
            return None
        else:
            return ast.Import(new_names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom | None:
        if node.module == "macro_in_python":
            return None
        else:
            return node

    def is_macro_decorator(self, node: ast.expr) -> bool:
        return isinstance(node, ast.Name) and node.id == "macro"

    def is_apply_decorator(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id == "apply":
                return True

        return False

    def visit_FunctionDef(
        self, node: ast.FunctionDef
    ) -> ast.FunctionDef | list[ast.stmt] | None:
        if node.name in self.macro_map:
            raise errors.FileMacroError(f"Macro {node.name} already defined.")

        if any(self.is_macro_decorator(d) for d in node.decorator_list):
            if len(node.decorator_list) != 1:
                raise errors.FileMacroError(
                    f"Macro {node.name} has decorator other than macro."
                )

            clean_node = deepcopy(node)
            clean_node.decorator_list = []
            names_map: dict[str, Any] = {}
            exec(ast.unparse(clean_node), {}, names_map)
            func = names_map[node.name]

            self.macro_map[node.name] = macro(func, node)

            return None

        elif any(self.is_apply_decorator(d) for d in node.decorator_list):
            n = len(node.decorator_list)
            if where(node.decorator_list, self.is_apply_decorator) != n - 1:
                raise errors.FileMacroError(
                    f"Function {node.name} has decorator before apply."
                )

            clean_node = deepcopy(node)
            clean_node.decorator_list = []
            names_map = {}
            exec(ast.unparse(clean_node), {}, names_map)
            func = names_map[node.name]

            new_node = deepcopy(node)

            apply_decorator = new_node.decorator_list.pop()
            assert isinstance(apply_decorator, ast.Call)

            args = []
            for arg in apply_decorator.args:
                if not isinstance(arg, ast.Name):
                    raise errors.FileMacroError(
                        f"Function {node.name} has non-macro argument: {arg}"
                    )
                if arg.id not in self.macro_map:
                    raise errors.FileMacroError(
                        f"Function {node.name} has non-macro argument: {arg.id}"
                    )

                args.append(self.macro_map[arg.id])

            new_node.body = apply_ast(func, *args, tree=clean_node).body

            return new_node

        return node


def convert_file(path: Path, output_path: Path) -> None:
    with open(path, "r") as f:
        code = f.read()

    t = ast.parse(code)
    FileConverter().visit(t)
    result = ast.unparse(t)

    with open(output_path, "w") as f:
        f.write(result)
