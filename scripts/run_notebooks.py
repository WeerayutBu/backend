import ast
import asyncio
import inspect
import json
from pathlib import Path


async def execute(path: Path) -> None:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__"}

    for index, cell in enumerate(notebook["cells"], start=1):
        if cell["cell_type"] != "code":
            continue

        code = compile(
            "".join(cell["source"]),
            f"{path}:cell-{index}",
            "exec",
            flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
        )
        result = eval(code, namespace)
        if inspect.isawaitable(result):
            await result


async def main() -> None:
    paths = sorted(Path().glob("0[1-7]-*/*.ipynb"))
    for path in paths:
        await execute(path)
        print(f"PASS {path}")

    print(f"Executed {len(paths)} notebooks")


if __name__ == "__main__":
    asyncio.run(main())
