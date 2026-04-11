---
description: aplicar la tarea correspondiente
---

[INSTRUCCIÓN MAESTRA]
Debes ejecutar la tarea técnica especificada por el usuario y documentar EXACTAMENTE los cambios realizados en el archivo de registro.

**Tarea a realizar:**
`{{TASK_ID}}` — {{TASK_DESCRIPTION}}

**Contexto Global OBLIGATORIO:**
Antes de realizar cualquier cambio:
1. Busca el `{{TASK_ID}}` en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{US_ID}}_tasks.md` para obtener el contexto técnico completo de la tarea: historia relacionada, criterios de aceptación y detalles de implementación.
2. Lee `.quinoto-spec/discovery/` para comprender el estado actual del proyecto (especialmente `00-stack-profile.md` para conocer el stack, comandos de test y convenciones).
3. Lee `.quinoto-spec/proposals/` para alinear tu código con las propuestas técnicas aprobadas.
4. Asegúrate de que esta tarea contribuya coherentemente a la arquitectura global.

**Instrucciones de Ejecución:**
1. **Confirmación requerida**: Antes de crear un branch, pregunta al usuario si desea crear uno nuevo. Si el usuario no quiere crear un branch, omite este paso y continúa trabajando en la rama actual.
2. Si el usuario confirma, crea un branch con el nombre `feature/{{TASK_ID}}-slug-descriptivo` en kebab-case (ej. `feature/US-ABC-001-add-login-endpoint`) usando la skill `generate-github-branch`.
2. Analiza el código actual y realiza los cambios necesarios para cumplir con la tarea descrita.
3. **Verificación de Criterios de Aceptación (DoD)**: Antes de finalizar, revisa uno a uno los criterios de aceptación definidos en la tarea/historia y confirma que cada uno está cumplido. Si alguno no está cubierto, impleméntalo o documenta la excepción.
4. **Ejecuta los tests del stack**: Usa el comando de tests detectado en `00-stack-profile.md` (ej. `npm test`, `pytest`, `bundle exec rspec`) y verifica que no haya regresiones. Si los tests fallan, corrígelos antes de continuar.

**Instrucciones de Documentación (Changelog):**
Una vez aplicados los cambios, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Tarea: {{TASK_ID}} — {{TASK_DESCRIPTION}}
- **Resumen**:
  - Lista de archivos modificados con el siguiente formato por cada uno:
    - `ruta/relativa/al/archivo` — [creado | modificado | eliminado] — motivo del cambio
  - Resumen técnico de la solución implementada.
  - Estado de los criterios de aceptación (DoD): ✅ cumplidos / ⚠️ excepciones documentadas.

**Instrucción Final OBLIGATORIA (Mark Done):**
Una vez completado y documentado el changelog, DEBES ejecutar la skill `quinotospec-mark-done` pasando:
- `TASK_ID`: el ID de la tarea completada.
Esto actualizará el estado de la tarea, la historia y la propuesta correspondiente.

**Blood-Bond Monitor:**
Después de `quinotospec-mark-done`, ejecutar skill `quinotospec-blood-bond-monitor --check-only`:
- Si `should_remind: true` (inactivo >=14 días), mostrar recordatorio pasivo con suggestions
- Si `should_remind: false`, no mostrar nada

IMPORTANTE: Los pasos de documentación y mark-done son OBLIGATORIOS. No termines la ejecución sin completarlos.

---

## Sugerencia de Siguiente Tarea

Después de completar una tarea y ejecutar `quinotospec-mark-done`, DEBES buscar y sugerir la siguiente tarea a ejecutar:

1. **Lee el archivo de tareas**: `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{US_ID}}_tasks.md` (deriva el `US_ID` del `{{TASK_ID}}` dado, ej. si TASK_ID es `TSK-AUTH-001`, la historia es `US-AUTH-XXX`)

2. **Encuentra la siguiente tarea**:
   - Recorre las tareas en orden (por su ID numérico)
   - Una tarea está lista para ejecutar si:
     - No está marcada como completada (`[ ]` en lugar de `[x]`)
     - Todas sus tareas dependientes están completadas
   - La primera tarea que cumpla estas condiciones es la siguiente

3. **Formula la sugerencia**:
   - Si hay una siguiente tarea: *"¿Deseas continuar con la tarea `{{NEXT_TASK_ID}}` — {{NEXT_TASK_TITLE}}?"*
   - Si no hay más tareas en esa historia: *"No hay más tareas pendientes en esta historia. ¿Deseas continuar con otra historia de usuario de la propuesta?"*
   - Si todas las tareas de la propuesta están completas: *"¡Felicidades! Todas las tareas de la propuesta '{{PROPOSAL_SLUG}}' han sido completadas."*

**Nota**: Si el archivo de tareas no existe o no se puede determinar la siguiente tarea, omite esta sugerencia silenciosamente.