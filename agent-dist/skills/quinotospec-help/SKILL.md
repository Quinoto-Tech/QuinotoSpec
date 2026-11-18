---
name: quinotospec-help
description: Navegacion contextual global — inspecciona .quinoto-spec/ desde cero y recomienda el siguiente comando exacto segun el estado real del proyecto.
---

> **Fuente de verdad:** esta skill contiene el prompt canónico; el comando `/quinotospec.help` delega aquí por archivo.

# Skill: Help

[INSTRUCCIÓN MAESTRA]
Debes inspeccionar el estado completo de `.quinoto-spec/` y responder con el siguiente paso accionable del ciclo Proposal First. No escribes archivos del proyecto: solo diagnosticas y guias.

**Parámetros:**

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `--json` | No | Emite el diagnóstico estructurado en lugar del resumen legible |
| `--root` `PATH` | No | Raíz del proyecto (por defecto `.`) |
| `--stale-days` `N` | No | Umbral de obsolescencia del discovery (por defecto `30`) |

**Invocación:**

```bash
@quinotospec.help
@quinotospec.help --json
@quinotospec.help --stale-days 60
```

---

## Paso 1 — Ejecutar el recomendador

```bash
python3 -B agent-dist/skills/quinotospec-help/help.py --root . --json
```

- Si el proyecto consumidor no tiene el script (instalación mínima), inspecciona manualmente:
  1. `.quinoto-spec/` existe.
  2. `.quinoto-spec/discovery/*.md` existe y su fecha.
  3. `.quinoto-spec/proposals/*/proposal.md`, `user-stories.md` y `*_tasks.md`.
  4. Checkboxes `- [ ]` / `- [x]` en los archivos de tareas.

## Paso 2 — Interpretar el estado

| Estado detectado | Recomendación |
|------------------|---------------|
| Sin `.quinoto-spec/` | `/quinotospec.init` y luego `/quinotospec.discovery` |
| Sin discovery | `/quinotospec.discovery` |
| Discovery > `stale-days` | `/quinotospec.refresh-discovery` |
| Sin propuestas activas | `/quinotospec.create-proposal` |
| Propuesta sin `user-stories.md` | `/quinotospec.create-user-stories {slug}` |
| Propuesta sin `*_tasks.md` | `/quinotospec.create-tasks {slug}` |
| Tareas pendientes | `/quinotospec.apply {TASK_ID}` |
| Todas las tareas completadas | `/quinotospec-mark-done {slug}` y `/quinotospec.archive {slug}` |
| Sin acciones pendientes | `/quinotospec.status` |

## Paso 3 — Responder al usuario

1. Presenta un resumen de 3-5 líneas: inicialización, discovery (vigente/obsoleto), propuestas activas y tareas pendientes.
2. Muestra el comando exacto recomendado en un bloque de código.
3. Si hay varias propuestas activas, lista el siguiente comando por cada una y marca cuál tiene prioridad.
4. Ofrece ejecutar el comando recomendado si el usuario lo confirma.

## Reglas

- Solo lectura. No modifiques artefactos ni estados.
- No inventes IDs: usa los que devuelva `help.py` o los que aparezcan literalmente en los archivos de tareas.
- Si `help.py` falla, degrada a inspección manual y reporta el error sin bloquear al usuario.
- No reemplaza `/quinotospec.status`: `help` responde "qué hago ahora", `status` muestra el dashboard completo.


## Cuando usar

- Al retomar un proyecto despues de dias o semanas
- Cuando no sabes si toca discovery, propuesta, stories, tareas o archivo
- Antes de `/quinotospec.status` si solo quieres el siguiente paso accionable
- En CI o scripts para verificar que el proyecto no quedo en un estado incompleto

## Invocacion

```bash
/quinotospec.help
/quinotospec.help --json
python3 -B agent-dist/skills/quinotospec-help/help.py --root . --json
```

## Comportamiento

`help.py` inspecciona, sin escribir nada:

| Senal | Fuente | Efecto |
|-------|--------|--------|
| Proyecto inicializado | `.quinoto-spec/` | Si falta, recomienda `init` + `discovery` |
| Discovery presente | `.quinoto-spec/discovery/*.md` | Si falta, recomienda `discovery` |
| Discovery obsoleto | mtime mas reciente > `--stale-days` (30 por defecto) | Recomienda `refresh-discovery` |
| Propuestas activas | `.quinoto-spec/proposals/*/proposal.md` | Si no hay, recomienda `create-proposal` |
| User stories | `proposals/{slug}/user-stories.md` | Si faltan, recomienda `create-user-stories` |
| Tareas | `proposals/{slug}/*_tasks.md` | Si faltan, recomienda `create-tasks` |
| Tareas pendientes | checkboxes `- [ ]` / `| [ ] |` con `TSK-*` | Recomienda `apply <TASK_ID>` |
| Tareas completadas | checkboxes `- [x]` | Recomienda `mark-done` y `archive` |

## Salida `--json`

```json
{
  "schema_version": 1,
  "initialized": true,
  "discovery": {"present": true, "files": 8, "age_days": 4, "stale": false},
  "proposals": {"active": 1, "archived": 0, "items": []},
  "recommendations": [
    {"command": "/quinotospec.apply TSK-AUTH-a1b2-001", "reason": "...", "priority": "high"}
  ],
  "next_command": "/quinotospec.apply TSK-AUTH-a1b2-001"
}
```

Las recomendaciones se ordenan por prioridad (`high`, `medium`, `low`) y `next_command` es siempre la primera.
