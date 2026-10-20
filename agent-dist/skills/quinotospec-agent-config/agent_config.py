#!/usr/bin/env python3
"""quinotospec-agent-config — merge 3-layer de configuracion de agentes.

Capas (la ultima gana):
    1. agent-dist/config/agent-defaults.toml      (shipped, no editar)
    2. .quinoto-spec/agent-team.toml              (versionado)
    3. .quinoto-spec/agent-personal.toml          (.gitignored)

Tambien acepta las rutas legacy `.quinoto-spec/_config/<archivo>.toml`.

Uso:
    agent_config.py --root . --list
    agent_config.py --root . --agent architect
    agent_config.py --root . --agent architect --json
"""

import argparse
import copy
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

try:  # Python 3.11+
    import tomllib as _toml  # type: ignore
except ImportError:  # pragma: no cover - fallback for Python 3.8-3.10
    _toml = None


class ConfigError(Exception):
    pass


def parse_scalar(raw):
    value = raw.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\n", "\n")
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item) for item in inner.split(",")]
    try:
        return int(value)
    except ValueError:
        return value


def parse_minimal_toml(text):
    """Parser TOML minimo para Python 3.8-3.10.

    Soporta tablas `[a.b]`, strings, ints, bools, arrays de escalares y
    comentarios. Los defaults del paquete se mantienen dentro de ese subset.
    """
    root = {}
    current = root
    for number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            names = [name.strip() for name in line[1:-1].split(".") if name.strip()]
            current = root
            for name in names:
                current = current.setdefault(name, {})
                if not isinstance(current, dict):
                    raise ConfigError("line {}: table conflicts with scalar".format(number))
            continue
        if "=" not in line:
            raise ConfigError("line {}: expected key = value".format(number))
        key, raw_value = line.split("=", 1)
        key = key.strip().strip('"')
        current[key] = parse_scalar(raw_value)
    return root


def load_toml(path):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ConfigError("cannot read {}: {}".format(path, error))
    if _toml is not None:
        try:
            return _toml.loads(text)
        except Exception as error:  # tomllib.TOMLDecodeError
            raise ConfigError("invalid TOML in {}: {}".format(path, error))
    return parse_minimal_toml(text)


def deep_merge(base, override):
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def layer_paths(root):
    state = root / ".quinoto-spec"
    candidates = [
        ("defaults", root / "agent-dist" / "config" / "agent-defaults.toml"),
        ("team", state / "agent-team.toml"),
        ("team", state / "_config" / "agent-team.toml"),
        ("personal", state / "agent-personal.toml"),
        ("personal", state / "_config" / "agent-personal.toml"),
    ]
    selected = {}
    for name, path in candidates:
        if path.is_file() and name not in selected:
            selected[name] = path
    return selected


def load_layers(root):
    layers = []
    merged = {}
    for name in ("defaults", "team", "personal"):
        selected = layer_paths(root)
        if name not in selected:
            continue
        path = selected[name]
        data = load_toml(path)
        if not isinstance(data, dict):
            raise ConfigError("{} must contain a TOML table".format(path))
        merged = deep_merge(merged, data)
        layers.append({"layer": name, "path": str(path)})
    return merged, layers


def config_for(merged, agent):
    agents = merged.get("agents", {})
    if not isinstance(agents, dict):
        raise ConfigError("'agents' must be a table")
    if agent not in agents:
        raise ConfigError(
            "unknown agent '{}' (available: {})".format(agent, ", ".join(sorted(agents)))
        )
    defaults = merged.get("defaults", {})
    base = copy.deepcopy(defaults.get("all", {})) if isinstance(defaults, dict) else {}
    return deep_merge(base, agents[agent])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Merge 3-layer de configuracion de agentes QuinotoSpec"
    )
    parser.add_argument("--root", default=".", help="Raiz del proyecto")
    parser.add_argument("--agent", help="Agente a resolver")
    parser.add_argument("--list", action="store_true", help="Listar agentes configurados")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print("ERROR: root not found: " + str(root), file=sys.stderr)
        return 2

    try:
        merged, layers = load_layers(root)
    except ConfigError as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 1

    agents = merged.get("agents", {})
    if not isinstance(agents, dict):
        print("ERROR: 'agents' must be a table", file=sys.stderr)
        return 1

    if args.list or not args.agent:
        listing = [
            {
                "agent": name,
                "display_name": value.get("display_name", name) if isinstance(value, dict) else name,
                "title": value.get("title", "") if isinstance(value, dict) else "",
            }
            for name, value in sorted(agents.items())
        ]
        if args.json:
            print(json.dumps({"schema_version": 1, "layers": layers, "agents": listing}, ensure_ascii=False, indent=2))
        else:
            print("Agentes configurados ({})".format(len(listing)))
            for item in layers:
                print("  capa {}: {}".format(item["layer"], item["path"]))
            for item in listing:
                print("  - {}: {} — {}".format(item["agent"], item["display_name"], item["title"]))
        return 0

    try:
        resolved = config_for(merged, args.agent)
    except ConfigError as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "agent": args.agent,
                    "layers": layers,
                    "config": resolved,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print("Agent: {}".format(args.agent))
        for item in layers:
            print("  capa {}: {}".format(item["layer"], item["path"]))
        print(json.dumps(resolved, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
