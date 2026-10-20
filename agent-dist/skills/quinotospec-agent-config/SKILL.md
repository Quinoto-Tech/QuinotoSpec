---
name: quinotospec-agent-config
description: Configuracion 3-layer de agentes — merge de agent-defaults.toml, agent-team.toml y agent-personal.toml con hot-reload sin editar archivos del paquete.
---

# Skill: Quinotospec Agent Config

> Los agentes traen una personalidad base; tu equipo y tu entorno personal la ajustan sin forks ni copias del paquete.

## Cuando usar

- Al incorporarte a un proyecto: definir el tono y las reglas del equipo
- Antes de `/quinotospec.party-mode` o `/quinotospec.battle-frenzy` para alinear voces
- Cuando un agente debe reforzar un principio local (por ejemplo, "siempre TypeScript estricto")
- Para auditar que configuracion efectiva tiene un agente

## Capas

| Capa | Archivo | Versionado | Proposito |
|------|---------|------------|-----------|
| 1. Defaults | `agent-dist/config/agent-defaults.toml` | Si (paquete) | Personalidad base de los 9 agentes. **No editar.** |
| 2. Equipo | `.quinoto-spec/agent-team.toml` | Si | Convenciones del equipo |
| 3. Personal | `.quinoto-spec/agent-personal.toml` | No (`.gitignore`) | Preferencias locales |

Merge: `defaults -> team -> personal`. La ultima capa que define una clave gana; las tablas se fusionan en profundidad.

Rutas legacy soportadas: `.quinoto-spec/_config/agent-team.toml` y `.quinoto-spec/_config/agent-personal.toml`.

## Invocacion

```bash
python3 -B agent-dist/skills/quinotospec-agent-config/agent_config.py --root . --list
python3 -B agent-dist/skills/quinotospec-agent-config/agent_config.py --root . --agent architect
python3 -B agent-dist/skills/quinotospec-agent-config/agent_config.py --root . --agent architect --json
```

## Ejemplo de override de equipo

```toml
# .quinoto-spec/agent-team.toml
[defaults.all.communication_style]
language = "espanol"
verbosity = "bajo"

[agents.code-reviewer]
principles = ["Bloquear cualquier PR sin tests", "Toda observacion debe venir con evidencia"]
```

## Ejemplo de override personal

```toml
# .quinoto-spec/agent-personal.toml  (.gitignored)
[agents.doc-writer.communication_style]
verbosity = "alto"
```

## Salida `--json`

```json
{
  "schema_version": 1,
  "agent": "architect",
  "layers": [
    {"layer": "defaults", "path": ".../agent-defaults.toml"},
    {"layer": "team", "path": ".../.quinoto-spec/agent-team.toml"}
  ],
  "config": {"display_name": "Alba", "title": "Arquitecta de Sistemas"}
}
```

## Reglas

- Nunca modificar `agent-dist/config/agent-defaults.toml` para personalizar: usar las capas 2/3.
- `agent-personal.toml` debe estar en `.gitignore`.
- Un TOML invalido debe fallar con mensaje claro y no aplicar una config parcial.
- Hot-reload: el helper se ejecuta en cada activacion; no se cachea entre invocaciones.
- El parser minimo (Python 3.8-3.10) soporta tablas, strings, ints, bools y arrays de escalares.
