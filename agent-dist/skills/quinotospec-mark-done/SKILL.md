---
name: quinotospec-mark-done
description: Automatiza el marcado de tareas como completadas, actualizando archivos de seguimiento y moviendo artefactos completados a la carpeta _archived/.
---

# Skill: Mark Done

Usa esta skill cuando el usuario indica que una tarea técnica (`TSK-MNEM-suffix-NNN`) ha sido completada. Antes de modificar estados, ejecuta `quinotospec-verify-before-done`; después actualiza los archivos de seguimiento usando el contrato común y, si el elemento está 100% completo, lo mueve a `_archived/`.

## Instrucciones de Ejecución

### Modo Individual

#### Paso 0 — Verificar antes de modificar estados

1. Ejecuta `quinotospec-verify-before-done` con el `TASK_ID` y la evidencia de la tarea.
2. Valida `.quinoto-spec/evidence/{{TASK_ID}}/verify-before-done.json` con `evidence_validate.py --kind verify-before-done --require --json`.
3. Revisa cada criterio DoD, tests, lint, typecheck y el diff.
4. Si falta evidencia o una verificación falla, detén el proceso y mantén la tarea en `in_progress` o `blocked`.
5. Solo después de un gate exitoso continúa marcando el checkbox o moviendo archivos.

#### Paso 1 — Marcar la tarea como completada

1. Ejecuta `python3 agent-dist/skills/quinotospec-contract/contract.py inspect --root . --json` y localiza el `canonical_id` de la tarea.
2. Busca el archivo `*_tasks.md` que contenga el task ID; no asumas que el nombre del archivo contiene el story ID.
3. Si el ID no existe, notifica al usuario y detén el proceso.
4. Cambia la columna `Estado` de `[ ]` a `[x]` para esa tarea. En legacy, cambia el checkbox o etiqueta de estado equivalente.

#### Paso 2 — Verificar completitud del archivo de tareas

- Consulta el contrato normalizado y cuenta tareas con `status: pending`, `blocked` o `unknown`.
- Si todas las tareas de la story tienen `status: completed`:
  1. Mueve el archivo a `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/_archived/{{TASKS_FILE}}`.
  2. Ve al Paso 3.
- Si aún quedan tareas pendientes, ve directo al Paso 4.

#### Paso 3 — Verificar completitud de la User Story

- Busca la story por el campo `Historia Relacionada` de las tareas, no por similitud numérica.
- Si todas las tareas de esa story están `completed` y no quedan stories con tareas pendientes:
  1. Mueve `user-stories.md` a `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/_archived/user-stories.md`.
  2. Actualiza el `**Estado:**` en `proposal.md` a `✅ Completada`.
  3. Ejecuta nuevamente el validador del contrato antes de archivar la propuesta completa.

#### Paso 4 — Registrar en el Changelog

Ejecuta la skill `quinotospec-update-changelog` con:
- **Título de la Acción**: Task Completed: {{TSK_ID}}
- **Resumen**: Se completó la tarea '{{TSK_ID}}' perteneciente a la historia '{{US_ID}}' en la propuesta '{{PROPOSAL_SLUG}}'.

### Modo Bulk (Múltiples Tareas)

#### Paso 0 — Verificar el lote

Ejecuta `quinotospec-verify-before-done` y valida `evidence_validate.py` para cada tarea antes de modificar cualquier checkbox. Si una tarea falla el gate, procesa solo las tareas permitidas y reporta el bloqueo de las demás.

Usa `--bulk` o `-b` para marcar múltiples tareas a la vez:

```bash
/quinotospec-mark-done TSK-AUTH-a1b2-001,TSK-AUTH-a1b2-002,TSK-AUTH-a1b2-003 --bulk
```

#### Paso 1 — Procesar lista de tareas

1. Recibe array de IDs de tareas: `[TSK-AUTH-a1b2-001, TSK-AUTH-a1b2-002, ...]`
2. Para cada ID:
   - Busca y marca como completada `[x]`
   - Acumula éxitos y errores

#### Paso 2 — Verificar completitud por US

Después de procesar todas las tareas:
- Para cada US afectada, verificar si todas sus tareas están completas
- Si US completa, mover a `_archived/`

#### Paso 3 — Consolidar Changelog

- Una sola entrada de changelog para todas las tareas
- **Título**: Bulk Task Completion: {{CANTIDAD}} tasks
- **Resumen**: Se completaron {{CANTIDAD}} tareas: {{LISTA_DE_IDS}}

### Modo Force (Forzar Archive)

Usa `--force` para mover a archive aunque no esté 100% completo:

```bash
/quinotospec-mark-done US-AUTH-a1b2-001 --force
```

⚠️ **Advertencia**: Esto archivará el archivo de tareas aunque tenga tareas pendientes.

## Validacion Pre-Completion

La validación completa se delega a `quinotospec-verify-before-done` y al contrato de evidencia:

1. Lee `01-stack-profile.md` para obtener los comandos del stack.
2. Ejecuta tests focalizados y, cuando el riesgo lo requiera, la suite completa.
3. Ejecuta lint y typecheck disponibles.
4. Asocia cada criterio DoD con evidencia fresca.
5. Si una comprobación falla o no puede ejecutarse, detén el cambio de estado y reporta el bloqueo.

`--skip-tests` solo puede usarse para una comprobación secundaria con confirmación explícita; nunca omite `quinotospec-verify-before-done`. Las tareas de documentación o configuración usan una validación determinista equivalente y deben justificar por qué no requieren un test de comportamiento.
## Flags

| Flag | Descripcion |
|------|-------------|
| `--bulk` `-b` | Procesar multiples tareas separadas por coma |
| `--force` `-f` | Forzar archivado sin declarar `completed`; requiere confirmación doble |
| `--skip-changelog` | No actualizar changelog (solo testing) |
| `--dry-run` | Simular sin hacer cambios reales |
| `--skip-tests` | Omitir solo una comprobación secundaria; no omite verify-before-done |

## Manejo de Errores

- Si los tests fallan -> No marcar como completada, listar failures
- Si el archivo de tareas no existe -> notificar: *"No se encontro el archivo de tareas para {{US_ID}} en la propuesta {{PROPOSAL_SLUG}}."*
- Si el ID de tarea no existe en el archivo -> notificar: *"El ID {{TSK_ID}} no fue encontrado en el archivo de tareas."*
- Si `_archived/` no existe, crealo antes de mover archivos.
- Si bulk y parcial falla -> reportar que tareas fallaron y cuales se completaron exitosamente
- Si `--force` se usa con tareas pendientes -> requiere confirmacion doble
