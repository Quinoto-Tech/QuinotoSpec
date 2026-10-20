---
name: quinotospec-help
description: Navegacion contextual global — inspecciona .quinoto-spec/ desde cero y recomienda el siguiente comando exacto segun el estado real del proyecto.
---

# Skill: Quinotospec Help — Navegacion Contextual

> Un copiloto de navegacion: mira todo `.quinoto-spec/` y te dice exactamente que ejecutar ahora, sin que tengas que recordar el ciclo Proposal First.

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

## Reglas

- Solo lectura: nunca crea, mueve ni modifica archivos del proyecto.
- No sustituye a `/quinotospec.status` (dashboard completo); es el "que hago ahora".
- Si no reconoce IDs de tarea, degrada a `/quinotospec.suggest-next {slug}` en vez de fallar.
