"""Protect the dependency direction represented by the layer folders."""

import ast
from pathlib import Path

APP = Path(__file__).parents[1] / "app"
LAYER_RULES = {
    "domain": ("app.application", "app.interface", "app.infrastructure"),
    "application": ("app.interface", "app.infrastructure"),
    "interface": ("app.infrastructure",),
    "infrastructure": ("app.interface",),
}
FRAMEWORKS = {
    "arq",
    "fastapi",
    "httpx",
    "jwt",
    "pwdlib",
    "pydantic",
    "pydantic_settings",
    "redis",
    "sqlalchemy",
    "tenacity",
}


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    modules = {
        name.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for name in node.names
    }
    modules.update(
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module
    )
    return modules


def matches(module: str, prefixes: tuple[str, ...]) -> bool:
    return any(module == prefix or module.startswith(f"{prefix}.") for prefix in prefixes)


def test_dependencies_do_not_cross_sideways_or_outward() -> None:
    violations = []
    for layer, forbidden in LAYER_RULES.items():
        for path in (APP / layer).glob("*.py"):
            for module in imports(path):
                if matches(module, forbidden):
                    violations.append(f"{path.relative_to(APP)} imports {module}")
    assert not violations, "\n".join(violations)


def test_inner_layers_do_not_import_frameworks() -> None:
    violations = []
    for layer in ("domain", "application"):
        for path in (APP / layer).glob("*.py"):
            for module in imports(path):
                if module.split(".")[0] in FRAMEWORKS:
                    violations.append(f"{path.relative_to(APP)} imports {module}")
    assert not violations, "\n".join(violations)
