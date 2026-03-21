---
name: Mark Done
description: Automatiza el marcado de tareas como completadas, actualizando archivos de seguimiento y moviendo artefactos completados a la carpeta _archived/.
---

# Skill: Mark Done

Usa esta skill cuando el usuario indica que una tarea técnica (`TSK-XXX`) ha sido completada. Actualiza los archivos de seguimiento y, si el elemento está 100% completo, lo mueve a `_archived/`.

## Instrucciones de Ejecución

### Paso 1 — Marcar la tarea como completada

1. Busca el `TSK-XXX` dado en el archivo de tareas correspondiente `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{US_ID}}_tasks.md`.
2. Si el ID no existe, notifica al usuario y detén el proceso.
3. Cambia el checkbox `[ ]` a `[x]` para esa tarea.

### Paso 2 — Verificar completitud del archivo de tareas

- Cuenta los checkboxes `[ ]` restantes en el archivo.
- Si **todas las tareas están completadas** (`[x]`):
  1. Mueve el archivo a `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/_archived/{{US_ID}}_tasks.md`.
  2. Ve al Paso 3.
- Si aún quedan tareas pendientes, ir directo al Paso 4.

### Paso 3 — Verificar completitud de la Historia de Usuario

- Busca el `{{US_ID}}` correspondiente en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md`.
- Si **todas las historias de usuario de la propuesta están completadas**:
  1. Mueve `user-histories.md` a `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/_archived/user-histories.md`.
  2. Actualiza el `**Estado:**` en `proposal.md` a `✅ Completada`.

### Paso 4 — Registrar en el Changelog

Ejecuta la skill `quinotospec-update-changelog` con:
- **Título de la Acción**: Task Completed: {{TSK_ID}}
- **Resumen**: Se completó la tarea '{{TSK_ID}}' perteneciente a la historia '{{US_ID}}' en la propuesta '{{PROPOSAL_SLUG}}'.

## Manejo de Errores

- Si el archivo de tareas no existe → notificar: *"No se encontró el archivo de tareas para {{US_ID}} en la propuesta {{PROPOSAL_SLUG}}."*
- Si el ID de tarea no existe en el archivo → notificar: *"El ID {{TSK_ID}} no fue encontrado en el archivo de tareas."*
- Si `_archived/` no existe, créalo antes de mover archivos.
