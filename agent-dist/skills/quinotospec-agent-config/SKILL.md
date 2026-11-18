---
name: quinotospec-agent-config
description: Configuracion 3-layer de agentes — merge de agent-defaults.toml, agent-team.toml y agent-personal.toml con hot-reload sin editar archivos del paquete.
---

> **Fuente de verdad:** esta skill contiene el prompt canónico; el comando `/quinotospec.agent-config` delega aquí por archivo.

# Skill: Agent Config

[INSTRUCCIÓN MAESTRA]
Debes ayudar al usuario a personalizar la personalidad y el comportamiento de los agentes de QuinotoSpec mediante las capas `agent-team.toml` y `agent-personal.toml`, sin modificar `agent-dist/config/agent-defaults.toml`.

**Parámetros:**

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `--agent` `NAME` | No | Configurar un agente especifico |
| `--team` | No | Escribir en `.quinoto-spec/agent-team.toml` (versionado) |
| `--personal` | No | Escribir en `.quinoto-spec/agent-personal.toml` (.gitignored) |
| `--show` | No | Mostrar la configuracion efectiva sin modificar nada |

**Invocación:**

```bash
@quinotospec.agent-config --show
@quinotospec.agent-config --agent code-reviewer --team
@quinotospec.agent-config --agent doc-writer --personal
```

---

## Paso 1 — Mostrar la configuracion actual

```bash
python3 -B agent-dist/skills/quinotospec-agent-config/agent_config.py --root . --list
python3 -B agent-dist/skills/quinotospec-agent-config/agent_config.py --root . --agent {NAME} --json
```

Presenta al usuario:

- Capas cargadas (defaults, team, personal).
- Personalidad, principios y estilo de comunicacion efectivos.
- Que claves provienen de cada capa (si el usuario pregunta).

## Paso 2 — Determinar la capa destino

| Situacion | Capa | Archivo |
|-----------|------|---------|
| Convencion del equipo (debe versionarse) | 2 | `.quinoto-spec/agent-team.toml` |
| Preferencia individual (no se commitea) | 3 | `.quinoto-spec/agent-personal.toml` |

Si el usuario no lo especifica, pregunta una vez. Nunca escribas en `agent-dist/config/agent-defaults.toml`.

## Paso 3 — Escribir el override

1. Verifica que `.quinoto-spec/` exista; si no, sugiere `/quinotospec.init`.
2. Crea el archivo con cabecera y solo las claves que el usuario pidio:

   ```toml
   # .quinoto-spec/agent-team.toml
   [agents.{NAME}]
   principles = ["...", "..."]
   ```

3. Si el archivo ya existe, fusiona preservando las claves previas (no lo reescribas completo).
4. Si la capa es personal, garantiza que `.quinoto-spec/agent-personal.toml` figure en `.gitignore`.

## Paso 4 — Verificar el merge

```bash
python3 -B agent-dist/skills/quinotospec-agent-config/agent_config.py --root . --agent {NAME} --json
```

- Confirma que `layers` incluye la capa nueva.
- Confirma que `config` refleja el override.
- Si el TOML es invalido, corrige antes de terminar: un archivo invalido no se aplica parcialmente.

## Paso 5 — Dejar rastro

1. Si la capa es de equipo, registrar la decision con `/quinotospec.update-changelog`.
2. Recordar al usuario que la configuracion se relee en cada activacion (hot-reload).

## Reglas

- No modificar nunca `agent-dist/config/agent-defaults.toml`.
- No commitear `agent-personal.toml`.
- No aplicar configuraciones parciales si el TOML falla al parsear.
- Describir el efecto observable del override (tono, verbosidad, principios extra), no solo el TOML.


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
