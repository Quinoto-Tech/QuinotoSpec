---
description: aplicar la tarea correspondiente
---

[INSTRUCCIÓN MAESTRA]
Debes ejecutar la tarea técnica especificada por el usuario y documentar EXACTAMENTE los cambios realizados en el archivo de registro.

**Tarea a realizar:**
`{{TASK_ID}}` — {{TASK_DESCRIPTION}}

**Contexto Global OBLIGATORIO:**
Antes de realizar cualquier cambio:
1. Busca el `{{TASK_ID}}` en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/tasks.md` para obtener el contexto técnico completo de la tarea: historia relacionada, criterios de aceptación y detalles de implementación.
2. Lee `.quinoto-spec/discovery/` para comprender el estado actual del proyecto (especialmente `00-stack-profile.md` para conocer el stack, comandos de test y convenciones).
3. Lee `.quinoto-spec/proposals/` para alinear tu código con las propuestas técnicas aprobadas.
4. Asegúrate de que esta tarea contribuya coherentemente a la arquitectura global.

**Instrucciones de Ejecución:**
1. Crea un branch con el nombre `feature/{{TASK_ID}}-slug-descriptivo` en kebab-case (ej. `feature/US-ABC-001-add-login-endpoint`) usando la skill `generate_github_branch`.
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

IMPORTANTE: Los pasos de documentación y mark-done son OBLIGATORIOS. No termines la ejecución sin completarlos.