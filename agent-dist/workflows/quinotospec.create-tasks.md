---
description: crea tareas a partir de historias de usuario
---

Este workflow genera un plan de tareas técnicas derivado de una historia de usuario específica.
Requiere que las historias (`user-histories.md`) ya hayan sido creadas.

**Parámetros Requeridos:**
- `PROPOSAL_SLUG`: El nombre de la carpeta de la propuesta (ej. `refactor-proposal-workflows`).
- `USER_STORY_ID`: El ID de la historia de usuario objetivo (ej. `US-REF-123`).

**Instrucciones:**
1. Lee el archivo `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md`.
2. Extrae la historia cuya ID coincida con `{{USER_STORY_ID}}`. Si no existe, fallar con mensaje claro.
3. Basado en ESA única historia, genera un desglose de tareas técnicas en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md`.
4. El formato de las tareas debe ser:
    - **Título**: Plan de Tareas ({{PROPOSAL_NAME}}).
    - Tabla con columnas: ID, Título, Descripción, Historia Relacionada, Estimación, Dependencias.
    - **IDs**: Extrae el prefijo de la historia de usuario (ej. si la historia es `US-{{PREFIX}}-XXX`) y úsalo para las tareas: `TSK-{{PREFIX}}-001`, `TSK-{{PREFIX}}-002`, etc.
    - **Historia Relacionada**: DEBE enlazar explícitamente al ID de la historia correspondiente (`{{USER_STORY_ID}}`).

**Notas de generación:**
- Solo genera tareas relacionadas directamente con la historia especificada; no incluyas tareas globales ni de documentación genérica.
- Si la historia contiene subtareas o criterios de aceptación numerados, intenta mapear cada criterio a una tarea separada cuando tenga sentido.

**Exclusión:**
- No generes tareas de "actualizar documentación" genéricas.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Tasks Generated: {{PROPOSAL_NAME}} ({{USER_STORY_ID}})
- **Resumen**: Se generó el plan de tareas para la propuesta '{{PROPOSAL_NAME}}', enfocadas en la historia '{{USER_STORY_ID}}', en .quinoto-spec/proposals/{{PROPOSAL_SLUG}}/