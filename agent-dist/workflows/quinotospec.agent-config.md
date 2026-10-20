---
description: Configuracion 3-layer de agentes — guia la creacion de overrides de equipo y personales sin editar el paquete.
---

# Workflow: Agent Config

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
