"""Utilidades compartidas por los scripts de skills (solo stdlib).

Centraliza dos bloques que estaban duplicados literalmente en varios scripts:

- ``resolve_root(argv, env_names)``: extrae ``--root`` de argv y resuelve la
  raiz del proyecto (flag > variables de entorno > cwd).
- ``load_module_from_path`` / ``load_contract_module``: cargan un modulo Python
  por ruta sin instalar paquetes.

Los scripts viven en ``agent-dist/skills/<skill>/<script>.py`` y agregan
``agent-dist/lib`` a ``sys.path`` antes de importar este modulo.
"""

import importlib.util
import os
import sys
from pathlib import Path


def resolve_root(argv, env_names=()):
    """Devuelve ``(root_path, argv_sin_root)``.

    ``--root PATH`` tiene prioridad; si no aparece, se prueban las variables de
    entorno de ``env_names`` en orden; el fallback es el directorio actual.
    """
    args = list(argv)
    root = None
    if "--root" in args:
        i = args.index("--root")
        if i + 1 < len(args):
            root = args[i + 1]
            del args[i:i + 2]
        else:
            del args[i:i + 1]
    if root is None:
        for name in env_names:
            root = os.environ.get(name)
            if root:
                break
    if root is None:
        root = "."
    return Path(root).resolve(), args


def load_module_from_path(path, module_name):
    """Carga un modulo Python por ruta con un nombre estable en ``sys.modules``."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_contract_module(script_file):
    """Carga ``agent-dist/skills/quinotospec-contract/contract.py`` desde un script de skill."""
    path = Path(script_file).resolve().parents[1] / "quinotospec-contract" / "contract.py"
    return load_module_from_path(path, "quinotospec_contract_shared")
