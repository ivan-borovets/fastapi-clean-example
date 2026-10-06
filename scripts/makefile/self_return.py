# The script is called from Makefile
import ast
import sys
from collections import Counter
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

RULE: Final = "self-return"
IGNORE_DIRECTIVE: Final = f"{RULE}: ignore"
SCOPE_BOUNDARY: Final = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef


@dataclass(frozen=True, slots=True, order=True)
class Violation:
    line: int
    column: int
    message: str

    def render(self, path: Path, rule_label: str) -> str:
        return f"{path}:{self.line}:{self.column}: {rule_label}: {self.message}"


def main(argv: Sequence[str]) -> int:
    roots = [Path(root) for root in argv]
    if not roots:
        raise SystemExit("usage: self_return.py DIR [DIR ...]")
    non_directories = [str(root) for root in roots if not root.is_dir()]
    if non_directories:
        raise SystemExit(f"self_return.py: no such directory: {', '.join(non_directories)}")

    label = highlight(RULE)
    found = 0
    for path in sorted({path for root in roots for path in root.rglob("*.py")}):
        try:
            violations = sorted(find_violations(path.read_text(encoding="utf-8-sig")))
        except (OSError, SyntaxError, UnicodeDecodeError) as error:
            raise SystemExit(f"self_return.py: cannot check {path}: {error}") from error

        for violation in violations:
            print(violation.render(path, label))
            found += 1

    if found == 0:
        return 0

    sys.stdout.flush()
    print(f'{RULE}: silence with "# {IGNORE_DIRECTIVE}"', file=sys.stderr)
    return 1


def find_violations(source: str) -> Iterator[Violation]:
    lines = source.split("\n")
    for class_def in (node for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ClassDef)):
        for method in walk_own_scope(class_def):
            if not isinstance(method, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            message = diagnose(method)
            if message is None or is_suppressed(method, lines):
                continue
            yield Violation(method.lineno, method.col_offset + 1, message)


def diagnose(method: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    returns = method.returns
    if returns is None:
        return None
    if mentions_self(returns):
        return "drop the quotes around Self" if quotes_only_self(returns) else None
    if not returns_receiver(method):
        return None
    return f"use Self instead of {ast.unparse(unquote(returns))}"


def returns_receiver(method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    is_factory = any(refers_to(decorator, "classmethod") for decorator in method.decorator_list)
    nodes = list(walk_own_scope(method))
    if rebinds(nodes, "cls" if is_factory else "self"):
        return False

    returned = [node.value for node in nodes if isinstance(node, ast.Return)]
    if not returned:
        return False
    if not is_factory:
        return all(isinstance(value, ast.Name) and value.id == "self" for value in returned)

    instances = names_built_from_cls(nodes)
    return all(is_cls_call(value) or (isinstance(value, ast.Name) and value.id in instances) for value in returned)


def is_suppressed(method: ast.FunctionDef | ast.AsyncFunctionDef, lines: Sequence[str]) -> bool:
    header = lines[method.lineno - 1 : max(method.body[0].lineno - 1, method.lineno)]
    return any(IGNORE_DIRECTIVE in line for line in header)


def mentions_self(annotation: ast.expr) -> bool:
    return any(refers_to(node, "Self") or quotes_self(node) for node in ast.walk(unquote(annotation)))


def quotes_self(node: ast.AST) -> bool:
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        return False
    return any(refers_to(inner, "Self") for inner in ast.walk(unquote(node)))


def quotes_only_self(annotation: ast.expr) -> bool:
    quoted = [node for node in ast.walk(annotation) if isinstance(node, ast.Constant) and quotes_self(node)]
    return bool(quoted) and all(only_self(unquote(node)) for node in quoted)


def only_self(annotation: ast.expr) -> bool:
    if isinstance(annotation, ast.BinOp):
        return only_self(annotation.left) and only_self(annotation.right)
    return refers_to(annotation, "Self") or (isinstance(annotation, ast.Constant) and annotation.value is None)


def rebinds(nodes: Sequence[ast.AST], name: str) -> bool:
    return any(isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Store) for node in nodes)


def names_built_from_cls(nodes: Sequence[ast.AST]) -> set[str]:
    names: set[str] = set()
    for node in nodes:
        if isinstance(node, ast.Assign) and is_cls_call(node.value):
            names.update(target.id for target in node.targets if isinstance(target, ast.Name))
        elif isinstance(node, ast.AnnAssign) and is_cls_call(node.value) and isinstance(node.target, ast.Name):
            names.add(node.target.id)

    bindings = Counter(node.id for node in nodes if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store))
    return {name for name in names if bindings[name] == 1}


def is_cls_call(node: ast.expr | None) -> bool:
    if isinstance(node, ast.IfExp):
        return is_cls_call(node.body) and is_cls_call(node.orelse)
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "cls"


def refers_to(node: ast.AST, name: str) -> bool:
    if isinstance(node, ast.Name):
        return node.id == name
    return isinstance(node, ast.Attribute) and node.attr == name


def unquote(annotation: ast.expr) -> ast.expr:
    if not isinstance(annotation, ast.Constant) or not isinstance(annotation.value, str):
        return annotation
    try:
        return ast.parse(annotation.value, mode="eval").body
    except SyntaxError:
        return annotation


def highlight(text: str) -> str:
    return f"\033[1;31m{text}\033[0m" if sys.stdout.isatty() else text


def walk_own_scope(node: ast.AST) -> Iterator[ast.AST]:
    for child in ast.iter_child_nodes(node):
        yield child
        if not isinstance(child, SCOPE_BOUNDARY):
            yield from walk_own_scope(child)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
