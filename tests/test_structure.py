"""Loyiha tuzilmasi: har bir handler routeri ulangan, modullar sintaksis jihatdan to'g'ri.

Bu test aiogram o'rnatilmagan muhitda ham ishlaydi (kod bajarilmaydi, faqat AST o'qiladi).
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDLERS = ROOT / "handlers"


def _defines_router(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "router" for t in node.targets):
            return True
    return False


def test_every_handler_router_is_included():
    root_init = (HANDLERS / "__init__.py").read_text(encoding="utf-8")
    missing = []
    for package in [p for p in HANDLERS.iterdir() if p.is_dir() and (p / "__init__.py").exists()]:
        init_text = (package / "__init__.py").read_text(encoding="utf-8")
        assert f"{package.name}.router" in root_init, f"{package.name} ildiz routerga ulanmagan"
        for module in package.glob("*.py"):
            if module.name == "__init__.py" or not _defines_router(module):
                continue
            ref = f"{module.stem}.router"
            if ref not in init_text and ref not in root_init:
                missing.append(str(module.relative_to(ROOT)))
    assert not missing, f"Ulanmagan routerlar: {missing}"


def test_fallback_router_is_last():
    tree = ast.parse((HANDLERS / "__init__.py").read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "include_routers"]
    assert calls, "include_routers topilmadi"
    last = calls[0].args[-1]
    assert isinstance(last, ast.Attribute) and getattr(last.value, "id", None) == "fallback"


def test_all_python_files_parse():
    for path in ROOT.rglob("*.py"):
        if ".venv" in path.parts:
            continue
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_no_echo_handler_and_no_pipfile():
    assert not (HANDLERS / "users" / "echo.py").exists()
    assert not (ROOT / "Pipfile").exists()


def test_env_is_ignored_and_dist_has_required_keys():
    assert ".env" in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    dist = (ROOT / ".env.dist").read_text(encoding="utf-8")
    for key in ("BOT_TOKEN=", "DEVELOPER_ID=", "DATABASE_URL=", "TIMEZONE=", "CASHBACK_MAX_USE_PERCENT="):
        assert key in dist
    # Namuna faylda haqiqiy token bo'lmasligi kerak
    assert "BOT_TOKEN=\n" in dist
