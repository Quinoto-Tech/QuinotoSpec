---
description: Navegacion contextual global — inspecciona .quinoto-spec/ y guia al usuario con el siguiente comando exacto.
---

# Workflow: Help

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
