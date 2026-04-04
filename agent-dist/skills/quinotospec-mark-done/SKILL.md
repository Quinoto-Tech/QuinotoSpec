---
name: Mark Done
description: Automatiza el marcado de tareas como completadas, actualizando archivos de seguimiento y moviendo artefactos completados a la carpeta _archived/.
---

# Skill: Mark Done

Usa esta skill cuando el usuario indica que una tarea técnica (`TSK-XXX`) ha sido completada. Actualiza los archivos de seguimiento y, si el elemento está 100% completo, lo mueve a `_archived/`.

## Instrucciones de Ejecución

### Modo Individual

#### Paso 1 — Marcar la tarea como completada

1. Busca el `TSK-XXX` dado en el archivo de tareas correspondiente `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{US_ID}}_tasks.md`.
2. Si el ID no existe, notifica al usuario y detén el proceso.
3. Cambia el checkbox `[ ]` a `[x]` para esa tarea.

#### Paso 2 — Verificar completitud del archivo de tareas

- Cuenta los checkboxes `[ ]` restantes en el archivo.
- Si **todas las tareas están completadas** (`[x]`):
  1. Mueve el archivo a `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/_archived/{{US_ID}}_tasks.md`.
  2. Ve al Paso 3.
- Si aún quedan tareas pendientes, ir directo al Paso 4.

#### Paso 3 — Verificar completitud de la Historia de Usuario

- Busca el `{{US_ID}}` correspondiente en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md`.
- Si **todas las historias de usuario de la propuesta están completadas**:
  1. Mueve `user-histories.md` a `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/_archived/user-histories.md`.
  2. Actualiza el `**Estado:**` en `proposal.md` a `✅ Completada`.

#### Paso 4 — Registrar en el Changelog

Ejecuta la skill `quinotospec-update-changelog` con:
- **Título de la Acción**: Task Completed: {{TSK_ID}}
- **Resumen**: Se completó la tarea '{{TSK_ID}}' perteneciente a la historia '{{US_ID}}' en la propuesta '{{PROPOSAL_SLUG}}'.

### Modo Bulk (Múltiples Tareas)

Usa `--bulk` o `-b` para marcar múltiples tareas a la vez:

```bash
/mark-done TSK-AUTH-001,TSK-AUTH-002,TSK-AUTH-003 --bulk
```

#### Paso 1 — Procesar lista de tareas

1. Recibe array de IDs de tareas: `[TSK-AUTH-001, TSK-AUTH-002, ...]`
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
/mark-done US-AUTH-001 --force
```

⚠️ **Advertencia**: Esto archivará el archivo de tareas aunque tenga tareas pendientes.

## Manejo de Errores

- Si el archivo de tareas no existe → notificar: *"No se encontró el archivo de tareas para {{US_ID}} en la propuesta {{PROPOSAL_SLUG}}."*
- Si el ID de tarea no existe en el archivo → notificar: *"El ID {{TSK_ID}} no fue encontrado en el archivo de tareas."*
- Si `_archived/` no existe, créalo antes de mover archivos.
- Si bulk y parcial falla → reportar qué tareas fallaron y cuáles succeedieron

## Flags

| Flag | Descripción |
|------|-------------|
| `--bulk` `-b` | Procesar múltiples tareas separadas por coma |
| `--force` `-f` | Forzar archive aunque no esté completo |
| `--skip-changelog` | No actualizar changelog (para testing) |
| `--dry-run` | Simular sin hacer cambios reales |
