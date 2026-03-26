"""
Module auto-discovery registry.

Scans all subdirectories under ``app/modules/`` for files matching
``controllers/*_controller.py`` and collects any ``APIRouter`` instances
found in those files.

Usage in ``main.py``::

    from app.modules import register_all_routers
    register_all_routers(app)
"""

import importlib
import os
import pkgutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, FastAPI


def _discover_routers() -> List[APIRouter]:
    """Walk modules/*/controllers/*_controller.py and collect routers."""
    routers: List[APIRouter] = []
    modules_dir = Path(__file__).parent

    for module_dir in sorted(modules_dir.iterdir()):
        # Skip __pycache__, _base, files, etc.
        if not module_dir.is_dir() or module_dir.name.startswith(("_", ".")):
            continue

        controllers_dir = module_dir / "controllers"
        if not controllers_dir.is_dir():
            continue

        for file in sorted(controllers_dir.iterdir()):
            if file.suffix == ".py" and file.stem.endswith("_controller"):
                # Build dotted module path: app.modules.<module>.controllers.<file>
                module_path = f"app.modules.{module_dir.name}.controllers.{file.stem}"
                try:
                    mod = importlib.import_module(module_path)
                    # Collect any APIRouter attribute named "router"
                    router = getattr(mod, "router", None)
                    if isinstance(router, APIRouter):
                        routers.append(router)
                except Exception as exc:
                    print(f"[WARNING] Failed to import {module_path}: {exc}")

    return routers


def register_all_routers(app: FastAPI) -> None:
    """Discover and register all module routers onto the FastAPI app."""
    routers = _discover_routers()
    for router in routers:
        app.include_router(router)
    print(f"[MODULES] Registered {len(routers)} module router(s)")
